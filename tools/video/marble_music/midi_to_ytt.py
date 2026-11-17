"""Export MIDI lyrics as optional .ytt karaoke or plain .srt/.vtt captions."""

import argparse
from html import escape
from io import StringIO
from itertools import groupby
import math
from pathlib import Path
from textwrap import fill
import xml.etree.ElementTree as ET

from midi_lyrics import phrase_end, read_phrases


def clipped_times(start, end, first, last, minimum=0):
    start_ms = max(minimum, round(max(start, first) * 1000))
    end_ms = round(min(end, last) * 1000)
    return start_ms, end_ms


def write_ytt(phrases, first, last, output):
    root = ET.Element('timedtext', format='3')
    head = ET.SubElement(root, 'head')
    style = {'b': '1', 'fo': '254', 'bc': '#161719', 'bo': '197'}
    ET.SubElement(head, 'pen', id='1', fc='#FAF8EF', **style)
    ET.SubElement(head, 'pen', id='2', fc='#FFDC70', **style)
    ET.SubElement(head, 'ws', id='1', ju='2', wfo='0')
    ET.SubElement(head, 'wp', id='1', ap='7', ah='50', av='82')
    body = ET.SubElement(root, 'body')
    body.text = '\n'
    count = 0
    for index, phrase in enumerate(phrases):
        onsets = list(dict.fromkeys(word.onset for word in phrase))
        for active, end in zip(onsets, onsets[1:] + [phrase_end(phrases, index)]):
            start_ms, end_ms = clipped_times(active, end, first, last, minimum=1)
            if start_ms >= end_ms:
                continue

            # Send the entire phrase with a new color state at each onset.
            cue = ET.SubElement(body, 'p', t=str(start_ms), d=str(end_ms - start_ms), wp='1', ws='1', p='1')
            runs = [(key, ' '.join(word.text for word in words))
                    for key, words in groupby(phrase, key=lambda word: '2' if word.onset == active else '1')]
            if len(runs) == 1:
                cue.set('p', runs[0][0])
                cue.text = runs[0][1]
            else:
                for span_index, (pen, text) in enumerate(runs):
                    span = ET.SubElement(cue, 's', p=pen)
                    span.text = text + (' ' if span_index + 1 < len(runs) else '')
                    if span_index == 0:
                        # Keep the first span's style through YouTube's upload conversion.
                        span.tail = '\u200b'
            cue.tail = '\n'
            count += 1
    if count:
        ET.ElementTree(root).write(output, encoding='unicode', xml_declaration=True)
    return count


def timecode(ms, separator):
    seconds, ms = divmod(ms, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    return f'{hours:02d}:{minutes:02d}:{seconds:02d}{separator}{ms:03d}'


def write_plain(phrases, first, last, output, webvtt):
    separator = '.' if webvtt else ','
    count = 0
    if webvtt:
        output.write('WEBVTT\n\n')
    previous_end = -1
    for index, phrase in enumerate(phrases):
        start, end = clipped_times(phrase[0].onset, phrase_end(phrases, index), first, last)
        # Some caption importers require a positive gap between adjacent cues.
        start = max(previous_end + 1, start)
        if start >= end:
            continue
        count += 1
        if not webvtt:
            output.write(f'{count}\n')
        lyric = fill(' '.join(word.text for word in phrase), width=42, break_long_words=False, break_on_hyphens=False)
        if webvtt:
            lyric = escape(lyric, quote=False)
        output.write(f'{timecode(start, separator)} --> {timecode(end, separator)}\n{lyric}\n\n')
        previous_end = end
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('midi', type=Path, help='MIDI file with lyric events')
    parser.add_argument('output', type=Path, help='output filename ending in .ytt, .srt or .vtt')
    parser.add_argument('--offset', type=float, default=0, help='seconds added to all MIDI times (e.g. 1.6 for the intro)')
    parser.add_argument('--start', type=float, default=0, help='first output second allowed to show lyrics')
    parser.add_argument('--end', type=float, help='last output second allowed to show lyrics')
    args = parser.parse_args()
    suffix = args.output.suffix.lower()
    if suffix not in ('.ytt', '.srt', '.vtt'):
        parser.error('Output must end in .ytt, .srt or .vtt')
    if not math.isfinite(args.offset) or not math.isfinite(args.start) or args.start < 0:
        parser.error('Offset must be finite and start must be finite and nonnegative')
    if args.end is not None and (not math.isfinite(args.end) or args.end <= args.start):
        parser.error('End must be finite and greater than start')
    phrases = read_phrases(args.midi, args.offset)
    if not phrases:
        parser.error('The MIDI contains no lyrics. Use the original lyric-bearing MIDI.')
    last = args.end if args.end is not None else math.inf

    content = StringIO()
    if suffix == '.ytt':
        count = write_ytt(phrases, args.start, last, content)
    else:
        count = write_plain(phrases, args.start, last, content, webvtt=suffix == '.vtt')
    if not count:
        parser.error('No lyrics in the selected output interval')
    with args.output.open('x', encoding='utf-8', newline='\n') as output:
        output.write(content.getvalue())
    print(f'{args.output}: {count} cues')


if __name__ == '__main__':
    main()
