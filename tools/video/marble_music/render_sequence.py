"""Render and assemble optional intro, MIDI performance and optional outro."""
import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import random
import re
import struct
import subprocess
import sys
from tempfile import TemporaryDirectory
import wave

from opening_title import frames_for_intro

HERE = Path(__file__).resolve().parent
SAMPLE_RATE = 48000
DEFAULT_FONTS = (
    '/System/Library/Fonts/Supplemental/Arial Bold.ttf',
    '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
)


def run(*command):
    subprocess.run(command, check=True)


def python(script, *args):
    run(sys.executable, HERE / script, *args)


def write_intro_audio(path, seconds):
    rng = random.Random(15)
    samples = bytearray()
    low = 0
    for n in range(round(seconds * SAMPLE_RATE)):
        t = n / SAMPLE_RATE
        low += 0.13 * (rng.uniform(-1, 1) - low)
        elapsed = t - 0.95
        sweep = 0.0
        if 0 < elapsed < 0.37:
            env = math.sin(math.pi * elapsed / 0.37) ** 2
            sweep = env * (0.07 * low + 0.018 * math.sin(math.tau * (230 * elapsed + 780 * elapsed ** 2)))
        ping = 0.0
        for at, pitch, amplitude in ((0.10, 1610, 0.016), (1.30, 2400, 0.028)):
            age = t - at
            if age > 0:
                ping += amplitude * math.sin(math.tau * pitch * age) * (1 - math.exp(-age * 900)) * math.exp(-age * 32)
        value = round((sweep + ping) * min(1, (seconds - t) / 0.03) * 32767)
        samples.extend(struct.pack('<hh', value, value))
    with wave.open(str(path), 'wb') as output:
        output.setparams((2, 2, SAMPLE_RATE, 0, 'NONE', 'not compressed'))
        output.writeframes(samples)


def render_frames(args, plan, destination, *options):
    run(args.blender, '-b', '--python-exit-code', '1', '-P', HERE / 'scene.py', '--',
        '--plan', plan, '--out', destination, '--look', args.look,
        '--res', args.res, '--samples', str(args.samples), '--device', args.device, *options)


def frame_files(directory, count):
    paths = [directory / f'{i:05d}.png' for i in range(count)]
    for path in paths:
        if not path.is_file() or not path.stat().st_size:
            raise ValueError(f'Missing rendered frame: {path}')
    return paths


def lyric_font(args):
    for name in (args.lyrics_font, args.title_font, *DEFAULT_FONTS):
        if name and Path(name).is_file():
            return name
    raise ValueError('Set --lyrics-font to the path of a TTF or OTF file')


def encode(args, stage, parts, music, intro_frames, played_frames, label_plan, label_frames):
    joined = stage / 'joined'
    joined.mkdir()
    for index, path in enumerate(parts):
        (joined / f'{index:05d}.png').symlink_to(path)

    inputs = ['-framerate', str(args.fps), '-i', joined / '%05d.png']
    inputs.extend(('-i', music))
    audio_label = f'[1:a]aresample={SAMPLE_RATE},aformat=channel_layouts=stereo,asetpts=PTS-STARTPTS'
    filters = []
    stream = 2
    if intro_frames:
        intro_audio = stage / 'intro.wav'
        write_intro_audio(intro_audio, intro_frames / args.fps)
        inputs.extend(('-i', intro_audio))
        filters.append(f'{audio_label}[music]')
        audio_label = f'[{stream}:a][music]concat=n=2:v=0:a=1'
        stream += 1
    samples = round(len(parts) * SAMPLE_RATE / args.fps)
    filters.append(f'{audio_label},apad,atrim=end_sample={samples},asetpts=N/SR/TB[a]')
    video = '[0:v]'
    if int(args.look[1:]) >= 5 and label_frames:
        labels = stage / 'labels'
        python('titles.py', label_plan, labels, '--res', args.res, '--end', str(label_frames - 1))
        inputs.extend(('-framerate', str(args.fps), '-i', labels / '%05d.png'))
        filters.extend((f'[{stream}:v]setpts=PTS+{intro_frames}[labels]',
                        f'{video}[labels]overlay=eof_action=pass:repeatlast=0[v_labels]'))
        video = '[v_labels]'
        stream += 1
    if args.lyrics_midi:
        captions = stage / 'captions'
        intro_seconds = intro_frames / args.fps
        python('lyrics_overlay.py', args.lyrics_midi, captions, '--font', lyric_font(args),
               '--fps', str(args.fps), '--frames', str(len(parts)),
               '--offset', str(intro_seconds - args.start), '--start', str(intro_seconds),
               '--end', str((intro_frames + played_frames) / args.fps))
        inputs.extend(('-framerate', str(args.fps), '-i', captions / '%05d.png'))
        width, height = map(int, args.res.split('x'))
        scale = min(width / 1080, height / 1920)
        cue_width, cue_height = max(2, round(880 * scale)), max(2, round(166 * scale))
        left, top = round(width * 0.475 - cue_width / 2), round(height * 0.76)
        filters.extend((f'[{stream}:v]scale={cue_width}:{cue_height}[lyrics]',
                        f'{video}[lyrics]overlay={left}:{top}:eof_action=pass:repeatlast=0[v_lyrics]'))
        video = '[v_lyrics]'

    encoded = stage / 'video.mp4'
    run('ffmpeg', '-v', 'error', '-nostdin', *inputs, '-filter_complex', ';'.join(filters),
        '-map', video, '-map', '[a]',
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '17', '-pix_fmt', 'yuv420p',
        '-c:a', 'aac', '-b:a', '256k', '-movflags', '+faststart', encoded)
    os.replace(encoded, args.output)
    print(f'Video: {args.output} ({len(parts)} frames at {args.fps} fps; {intro_frames} intro frames)')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('plan', type=Path)
    parser.add_argument('music', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--blender', default='blender')
    parser.add_argument('--start', type=float, required=True)
    parser.add_argument('--end', type=float, required=True)
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--samples', type=int, default=12)
    parser.add_argument('--res', default='1080x1920')
    parser.add_argument('--look', default='v5')
    parser.add_argument('--device', default='AUTO')
    parser.add_argument('--intro', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--outro', action=argparse.BooleanOptionalAction, default=False)
    parser.add_argument('--intro-title', default='Jingle Bells')
    parser.add_argument('--intro-subtitle', default='One Marble. Six Instruments.')
    parser.add_argument('--outro-title', default='Merry Christmas!')
    parser.add_argument('--outro-subtitle', default='@LucaMarbleMusic')
    parser.add_argument('--title-font', default='')
    parser.add_argument('--lyrics-midi', type=Path)
    parser.add_argument('--lyrics-font', default='')
    args = parser.parse_args()

    if not re.fullmatch(r'v\d+', args.look):
        parser.error('--look must have the form v5')
    if args.fps < 1:
        parser.error('--fps must be positive')
    if args.intro and not (args.intro_title.strip() or args.intro_subtitle.strip()):
        parser.error('The intro needs at least one line of text')
    if args.outro and not (args.outro_title.strip() or args.outro_subtitle.strip()):
        parser.error('The outro needs at least one line of text')
    if args.title_font and not Path(args.title_font).is_file():
        parser.error(f'Title font not found: {args.title_font}')
    if not args.title_font and (args.intro or args.outro):
        args.title_font = next((name for name in DEFAULT_FONTS if Path(name).is_file()), '')
    args.output = args.output.resolve()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.plan = args.plan.resolve()
    base = json.loads(args.plan.read_text())
    if base['fps'] != args.fps:
        parser.error('--fps must match the MIDI plan')
    if not base['keys'] or len(base['marble']) < 2:
        parser.error('The MIDI plan must contain a hit and at least two frames')

    played_frames = round((args.end - args.start) * args.fps)
    if not 1 <= played_frames <= len(base['marble']):
        parser.error('Requested MIDI duration does not fit the plan')
    with TemporaryDirectory(prefix='assemble-', dir=args.output.parent) as temporary:
        stage = Path(temporary)
        plan, music = args.plan, args.music
        body_count = played_frames
        label_frames = played_frames
        if args.outro:
            plan = stage / 'with_outro.json'
            sfx = stage / 'with_outro.sfx.json'
            python('ending.py', args.plan, plan, '--subscribe', '--line1', args.outro_title,
                   '--line2', args.outro_subtitle, '--line2-width', '0.36',
                   '--sub-wait', '0.5', '--sub-rise', '0.5', '--sub-hold', '1.2',
                   '--font', args.title_font)
            ending_plan = json.loads(plan.read_text())
            body_count = len(ending_plan['marble'])
            label_frames = min(played_frames, ending_plan['ending']['frame_last_hit'] + 1)
            cues = json.loads(sfx.read_text())
            cues['duration'] = max(played_frames, body_count) / args.fps
            sfx.write_text(json.dumps(cues))
            music = stage / 'ending_mix.wav'
            python('ending_sfx.py', args.music, sfx, music, '--chime-db', '-12')

        # A separate cache for each scene prevents resuming an outro render with MIDI-only frames.
        scene_hash = hashlib.sha256(plan.read_bytes())
        render_settings = (args.look, args.res, args.samples, args.title_font)
        scene_hash.update(repr(render_settings).encode())
        if args.title_font:
            scene_hash.update(Path(args.title_font).read_bytes())
        for script in ('scene.py', 'opening_title.py', 'ending_pad.py'):
            scene_hash.update((HERE / script).read_bytes())
        cache = args.output.parent / 'sequence_frames' / scene_hash.hexdigest()[:24]
        main_folder = cache / 'performance'
        render_frames(args, plan, main_folder, '--end', str(body_count - 1))
        performance = frame_files(main_folder, body_count)
        performance.extend([performance[-1]] * max(0, played_frames - body_count))

        intro = []
        if args.intro:
            title_key = hashlib.sha256(repr((args.intro_title, args.intro_subtitle)).encode()).hexdigest()[:16]
            folder = cache / f'intro_{title_key}'
            render_frames(args, plan, folder, '--intro', '--intro-title', args.intro_title,
                          '--intro-subtitle', args.intro_subtitle, '--intro-font', args.title_font)
            intro = frame_files(folder, frames_for_intro(args.fps))
        encode(args, stage, intro + performance, music, len(intro), played_frames, plan, label_frames)


if __name__ == '__main__':
    main()
