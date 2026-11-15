"""Synthesised marble-landing SFX for ending.py + final audio mix.
Main hit = glass marble on a lacquered pad: broadband click transient + inharmonic glass ring modes + wooden body knock + a
little low thump + a short room tail. Hop ticks (cues 'hops': [[t, linear gain], ...]) for the small bounces on the pad; legacy 'bounce2' = one off-screen tick.
Subscribe variant: cues 'whoosh' [t0, t1] (rising airy sweep while the marble lifts/falls), 'chime' t (soft bell shimmer on the
burst) and, for the fall style, 'settle' t (soft low metallic thunk when the text lands on the wall).
usage: python ending_sfx.py MUSIC.wav plan_end.sfx.json OUT.wav [--gain-db -4] [--tick-db -13] [--fade 0.6] [--sfx-only sfx.wav]
MUSIC.wav must start at t=0 of the song (e.g. h196_master.wav); output is trimmed to the ending duration and NOT yet
loudness-normalised (run ffmpeg loudnorm I=-14:TP=-1 afterwards, as for the rest of the pipeline)."""
import json, argparse, wave, numpy as np
ap = argparse.ArgumentParser(); ap.add_argument('music'); ap.add_argument('cues'); ap.add_argument('out')
ap.add_argument('--gain-db', type=float, default=-4.0, help='main hit peak level (dBFS) before loudnorm')
ap.add_argument('--tick-db', type=float, default=-13.0, help='second tick peak level (dBFS); <= -60 disables')
ap.add_argument('--fade', type=float, default=0.6); ap.add_argument('--chime-db', type=float, default=-9.0); ap.add_argument('--whoosh-db', type=float, default=-16.0); ap.add_argument('--settle-db', type=float, default=-15.0, help="fall style: soft thunk when the text lands ('settle' cue)"); ap.add_argument('--sfx-only', default=''); ap.add_argument('--seed', type=int, default=7)
a = ap.parse_args(); rng = np.random.default_rng(a.seed)

def hit(sr, scale=1.0, thump=1.0, bright=1.0):
    n = int(sr * 0.45); t = np.arange(n) / sr; y = np.zeros(n)
    cl = rng.standard_normal(int(sr * 0.0025)) * np.exp(-np.arange(int(sr * 0.0025)) / (sr * 0.0005))   # click transient
    cl = np.diff(cl, prepend=0); y[:len(cl)] += 0.9 * cl * bright
    for f, d, g in [(3150, 0.020, 0.55), (5870, 0.012, 0.40), (8420, 0.008, 0.28), (11200, 0.005, 0.18)]:   # glass ring (inharmonic)
        f *= scale; y += g * bright * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / d)
    for f, d, g in [(410, 0.050, 0.55), (760, 0.035, 0.45), (1270, 0.022, 0.35), (1980, 0.014, 0.25)]:      # lacquered wood knock
        f *= scale; y += g * np.sin(2 * np.pi * f * t + rng.uniform(0, 6.28)) * np.exp(-t / d)
    ph = 2 * np.pi * np.cumsum(95 + 60 * np.exp(-t / 0.012)) / sr                                           # low thump, slight pitch drop
    y += 0.8 * thump * np.sin(ph) * np.exp(-t / 0.065) * (1 - np.exp(-t / 0.0015))
    ir = rng.standard_normal(int(sr * 0.25)) * np.exp(-np.arange(int(sr * 0.25)) / (sr * 0.055))           # small-room tail
    y = y + 0.04 * np.convolve(y, ir)[:n]
    att = np.minimum(1, t / 0.0004); y *= att
    return y / np.max(np.abs(y))

w = wave.open(a.music); sr, ch, sw = w.getframerate(), w.getnchannels(), w.getsampwidth(); assert sw == 2
x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float64).reshape(-1, ch) / 32768; w.close()
C = json.load(open(a.cues)); N = int(round(C['duration'] * sr))
if len(x) < N: x = np.vstack([x, np.zeros((N - len(x), ch))])
x = x[:N].copy(); nf = int(a.fade * sr); x[-nf:] *= np.linspace(1, 0, nf)[:, None] ** 2
S = np.zeros((N, 2))
def place(y, t0, db, pan=0.0):
    i = int(round(t0 * sr)); y = y[:max(0, N - i)] * 10 ** (db / 20); L, R = np.cos((pan + 1) * np.pi / 4), np.sin((pan + 1) * np.pi / 4)
    S[i:i + len(y), 0] += y * L * 1.414; S[i:i + len(y), 1] += y * R * 1.414
place(hit(sr), C['contact'], a.gain_db, 0.0)
if a.tick_db > -60 and C.get('bounce2', 99) < C['duration'] - 0.1: place(hit(sr, 1.12, 0.35, 0.8), C['bounce2'], a.tick_db, -0.05)
for i, (t_, gl) in enumerate(C.get('hops', [])):
    if t_ < C['duration'] - 0.05: place(hit(sr, 1.05 + 0.05 * i, 0.4 / (i + 1), 0.9), t_, a.gain_db + 20 * np.log10(gl), 0.0)
def whoosh(dur):
    n = int(sr * dur); t = np.arange(n) / sr; y = rng.standard_normal(n); out = np.zeros(n); lo = 0.0; bp = 0.0
    fc = 300 * (12 ** (t / dur)); env = np.sin(np.pi * np.minimum(1, t / dur * 0.85)) ** 2 * (t / dur) ** 0.7
    for k in range(n):                                   # 2-pole state-variable band-pass with a rising centre
        f = 2 * np.sin(np.pi * fc[k] / sr); hp = y[k] - lo - 0.7 * bp; bp += f * hp; lo += f * bp; out[k] = bp
    out *= env; return out / np.max(np.abs(out))
def chime(dur=1.8):
    n = int(sr * dur); t = np.arange(n) / sr; y = np.zeros(n)
    for f0, g0, dly in [(1046.5, 1.0, 0.0), (1318.5, 0.7, 0.045), (1568.0, 0.6, 0.09), (2093.0, 0.45, 0.135)]:   # C6-E6-G6-C7 arpeggiated bell
        tt = np.clip(t - dly, 0, None); on = (t >= dly)
        for ratio, gp, d in [(1, 1, 0.9), (2.76, 0.35, 0.35), (5.4, 0.15, 0.15)]:
            y += on * g0 * gp * np.sin(2 * np.pi * f0 * ratio * tt) * np.exp(-tt / d) * (1 - np.exp(-tt / 0.002))
    sp = np.zeros(n)                                     # sparkle: tiny random high pings
    for k in range(14):
        i0 = int(sr * rng.uniform(0.02, 0.7)); f = rng.uniform(3500, 7000); m = min(n - i0, int(sr * 0.12)); tt = np.arange(m) / sr
        sp[i0:i0 + m] += rng.uniform(0.1, 0.25) * np.sin(2 * np.pi * f * tt) * np.exp(-tt / 0.03)
    return (y + sp) / np.max(np.abs(y + sp))
if 'whoosh' in C: place(whoosh(C['whoosh'][1] - C['whoosh'][0] + 0.05), C['whoosh'][0], a.whoosh_db)
if 'settle' in C and C['settle'] < C['duration'] - 0.05: place(hit(sr, 0.62, 0.9, 0.35), C['settle'], a.settle_db, 0.0)
if 'chime' in C:
    ch_ = chime(); place(ch_, C['chime'], a.chime_db, -0.15); place(ch_ * 0.6, C['chime'] + 0.012, a.chime_db - 4, 0.3)
if ch == 1: x = np.repeat(x, 2, 1)
y = x[:, :2] + S; pk = np.max(np.abs(y))
if pk > 0.97: y *= 0.97 / pk
def wr(path, d):
    o = wave.open(path, 'wb'); o.setnchannels(2); o.setsampwidth(2); o.setframerate(sr); o.writeframes((np.clip(d, -1, 1) * 32767).astype(np.int16).tobytes()); o.close()
wr(a.out, y)
if a.sfx_only: wr(a.sfx_only, S)
print(f"mixed {N/sr:.3f}s; hit at {C['contact']:.3f}s ({a.gain_db} dBFS); hops {C.get('hops')}; whoosh {C.get('whoosh')}; chime {C.get('chime')}; pre-norm peak {20*np.log10(pk):.1f} dBFS")
