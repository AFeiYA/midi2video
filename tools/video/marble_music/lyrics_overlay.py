"""Build frame-aligned transparent karaoke captions from MIDI lyric events."""

import argparse
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from midi_lyrics import phrase_end, read_phrases

WIDTH, HEIGHT = 880, 166
SIDE_PADDING = 34
REFERENCE_FONT_SIZE = 50


def lay_out(phrase, font_path):
    for size in range(REFERENCE_FONT_SIZE, 19, -1):
        font = ImageFont.truetype(font_path, size)
        rows = [[]]
        for word in phrase:
            proposed = ' '.join(entry.text for entry in (*rows[-1], word))
            if rows[-1] and font.getlength(proposed) > WIDTH - 2 * SIDE_PADDING:
                rows.append([])
            rows[-1].append(word)
        if len(rows) <= 2:
            return font, rows
    raise ValueError('Lyric phrase does not fit in two lines')


def draw_caption(font, rows, active, path):
    image = Image.new('RGBA', (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    step = font.size + 7
    box_height = step * len(rows) + 30
    top = (HEIGHT - box_height) // 2
    widths = [font.getlength(' '.join(w.text for w in row)) for row in rows]
    box_width = round(max(widths)) + SIDE_PADDING
    left = (WIDTH - box_width) // 2
    draw.rounded_rectangle((left, top, WIDTH - left, HEIGHT - top), radius=23, fill=(22, 23, 25, 197))
    for line, row in enumerate(rows):
        x = (WIDTH - widths[line]) / 2
        y = (HEIGHT - step * (len(rows) - 1)) / 2 + step * line
        for word in row:
            color = (255, 220, 112, 255) if word.onset == active else (250, 248, 239, 255)
            draw.text((x, y), word.text, font=font, fill=color, anchor='lm')
            x += font.getlength(word.text + ' ')
    image.save(path)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('midi', type=Path)
    parser.add_argument('output', type=Path)
    parser.add_argument('--font', required=True)
    parser.add_argument('--offset', type=float, default=0.0)
    parser.add_argument('--start', type=float, default=0.0, help='first output second allowed to show lyrics')
    parser.add_argument('--end', type=float, default=None, help='clear lyrics at this output second')
    parser.add_argument('--fps', type=int, default=30)
    parser.add_argument('--frames', type=int, required=True)
    args = parser.parse_args()

    phrases = read_phrases(args.midi, args.offset)
    if not phrases:
        parser.error('The MIDI contains no lyrics')

    args.output.mkdir()
    assets = args.output / 'assets'
    assets.mkdir()
    blank = assets / 'blank.png'
    Image.new('RGBA', (WIDTH, HEIGHT)).save(blank)
    schedule = [blank] * args.frames

    def frame(seconds):
        return min(args.frames, max(0, round(seconds * args.fps)))

    word_count = 0
    for index, phrase in enumerate(phrases):
        font, rows = lay_out(phrase, args.font)
        word_count += len(phrase)
        cues = list(dict.fromkeys(word.onset for word in phrase))
        end = phrase_end(phrases, index)
        for cue, (start, stop) in enumerate(zip(cues, cues[1:] + [end])):
            start_frame = frame(max(start, args.start))
            stop_frame = frame(min(stop, args.end) if args.end is not None else stop)
            if start_frame >= stop_frame:
                continue
            caption = assets / f'{index:03d}-{cue:02d}.png'
            draw_caption(font, rows, start, caption)
            schedule[start_frame:stop_frame] = [caption] * (stop_frame - start_frame)
    for index, source in enumerate(schedule):
        (args.output / f'{index:05d}.png').symlink_to(source.relative_to(args.output))
    print(f'{len(phrases)} phrases, {word_count} words, first lyric at {phrases[0][0].onset:.3f}s')


if __name__ == '__main__':
    main()
