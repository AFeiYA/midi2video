"""Read timed phrases and assemble syllables from MIDI lyrics events."""

from dataclasses import dataclass

import mido

LAST_WORD_HOLD = 0.82


@dataclass
class Word:
    text: str
    onset: float


def read_phrases(midi_path, offset):
    midi = mido.MidiFile(midi_path)
    tempo = 500000
    seconds = offset
    phrase = []
    word = ''
    onset = seconds
    phrases = []
    for event in mido.merge_tracks(midi.tracks):
        seconds += mido.tick2second(event.time, midi.ticks_per_beat, tempo)
        if event.type == 'set_tempo':
            tempo = event.tempo
        if event.type != 'lyrics':
            continue
        fragment = event.text.strip()
        if fragment:
            if not word:
                onset = seconds
            if fragment.endswith('-'):
                word += fragment if fragment.casefold() in ('one-', 'two-') else fragment[:-1]
            else:
                phrase.append(Word(word + fragment, onset))
                word = ''
        if '\n' in event.text:
            if word:
                phrase.append(Word(word, onset))
                word = ''
            if phrase:
                phrases.append(phrase)
                phrase = []
    if word:
        phrase.append(Word(word, onset))
    if phrase:
        phrases.append(phrase)
    return phrases


def phrase_end(phrases, index):
    end = phrases[index][-1].onset + LAST_WORD_HOLD
    if index + 1 < len(phrases):
        end = min(end, phrases[index + 1][0].onset)
    return end
