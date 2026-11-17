# Descending-layer hscroll, plus one passive guide

This is an optional 16:9 template. It does not replace portrait zigzag, hscroll v1, hscroll v2, or `landscape/`.

Strikes are frictionless and passive: restitution is at most 1, so a plate never adds kinetic energy. Seeded noise only reorders candidates that already obey that bound. Layers open downward. Inside a layer the marble may lob, fold left/right, or shuttle, including a local rise, when the incoming speed pays for it. A long note is the ballistic arc onto the next lower layer. The camera may follow right and down. The song is not held in a fixed height band.

The checked-in excerpt is the first 9 seconds of `projects/jingle-bells-marble-music/source/jingle_remix_6inst_16beat.mid` (melody tracks, 22 hits). That is not a whole-song proof. The 0–14 second window was not certified: the bounded search does not always find a passive clearance-clean route, and the gap is reported instead of raising restitution. The inst64 file `/workspace/marble/inst64/01_Jingle_Bells_64_Instruments_SingleStaff_Relay.mid` is not on this machine.

## Free-flight excerpt

From the repository root:

```bash
python3 tools/video/marble_music/extract_hits.py \
  projects/jingle-bells-marble-music/source/jingle_remix_6inst_16beat.mid \
  --start 0 --end 9 \
  -o tools/video/marble_music/hscroll_descent/examples/jingle_remix_0_9_melody.hits.json

cd tools/video/marble_music
python3 -m hscroll_descent.plan \
  hscroll_descent/examples/jingle_remix_0_9_melody.hits.json \
  -o hscroll_descent/examples/descent_excerpt_plan.json \
  --seed 2 --tilt-max 60 --patterns fold,fold,compact,shuttle \
  --report hscroll_descent/examples/descent_excerpt_audit.json
python3 -m hscroll_descent.diagram \
  hscroll_descent/examples/descent_excerpt_plan.json \
  hscroll_descent/examples/descent_excerpt_diagram.svg
python3 -m unittest hscroll_descent.test_descent -v
```

Equivalent integration entry, after `cd tools/video/marble_music`:

```bash
python3 plan_hscroll.py hscroll_descent/examples/jingle_remix_0_9_melody.hits.json \
  --style descent --seed 2 --tilt-max 60 --patterns fold,fold,compact,shuttle \
  -o hscroll_descent/examples/descent_excerpt_plan.json
```

`plan_zigzag.py --layout hscroll` forwards to `plan_hscroll.py`, so `--style descent` works there too.

### What passed, and what did not

| Check | Excerpt result |
|---|---|
| Contact time equals the MIDI time | yes |
| Flight is the gravity parabola, including between frames | yes |
| Approach from the free side, departure into it, normal along the impulse | yes |
| Specific energy does not rise at a strike | yes |
| Continuous capsule-proxy gap | yes, see the audit JSON |
| Full triangle mesh | not run |
| `check_keepout.py` / `check_pairs.py` probe points | not run |
| Whole song, or the missing inst64 MIDI | not run |
| Video | not run |

The capsule is the contact bar (half-length `--plate-half`, default 0.15 m, radius 0.045 m). Instrument bodies extend past it. A proxy pass is not a mesh pass.

v1's `--max-drop` is ignored. `--descent-max-drop` asks whether a shallower landing exists. If it does not, the command exits 2 and writes `*.impossible.json` with the energy deficit. It does not raise restitution.

## Passive guide (not rendered)

`rail.py` is one transition across the remix's 1.22449 s long note. It is not substituted into the 22-hit plan and `scene.py` does not read it.

Sequence, in order:

1. The strike has already given the marble velocity. It is not released from rest.
2. Free fall. Gravity increases the speed. Spin, if any, stays constant and does not push the center of mass.
3. Slip capture. Kinetic friction (μ = 0.40) runs until `v = ω R` for a solid sphere (`I = 2/5 m R²`). Position, speed, and spin are continuous. The friction does negative work. This is an impact-like dissipation spread over a short distance, not the later constraint force.
4. Captive circular groove. The normal is a constraint force. Static friction maintains rolling. Both do no work while the contact point is instantaneously at rest, so `½(1+2/5)v² + g z` is constant. The path goes down through a valley and up an exit lip. Samples are allowed to rise.
5. The groove ends. Velocity is the tangent. The remaining time is a free flight to a falling contact below the start.

A lip above that budget returns `cannot_crest_lip` and a positive deficit. No spring is added. A static deflector is the separate one-plate impulse in `static_deflector`; restitution above 1 is reported as a powered kicker and refused.

```bash
cd tools/video/marble_music
python3 -m hscroll_descent.rail --dt 1.22449 \
  -o hscroll_descent/examples/rail_transition.json \
  --svg hscroll_descent/examples/rail_transition.svg
```

### Mechanisms this follows

- US5007876A, banked hairpin marble race toy: a U-turn reverses the marble and the track is banked through that turn. Here the wall toward the back of the stage is taller through the hairpin. This is not that toy.
- US4874342A, jump chute marble race toy: a downhill speed run ends in an upturned lip and the marble leaves on a free trajectory. The lip in this plan is that idea. This is not that toy.
- OpenStax, *University Physics Volume 1*, section 11.1, [Rolling Motion](https://openstax.org/books/university-physics-volume-1/pages/11-1-rolling-motion): rolling energy is translation plus rotation, and static friction does no work because the contact point is instantaneously at rest. Kinetic friction while slipping does negative work.
- Pinball habitrails are passive wire guides. A vertical up-kicker is powered and is not used. [Flipcommons](https://flipcommons.org/gameplay-features/habitrails), [Pinside on return speed](https://pinside.com/pinball/forum/topic/what-rampshabitrails-return-the-ball-at-full-speed).

## Renderable guide inside the 9 second excerpt

Hit 9 to hit 10 (1.22449 s) is the guide. The marble already has velocity. The fall increases speed. The channel turns left, dips, and climbs a short lip inside the rolling budget. The tangent jump lands on the next MIDI onset. Later notes keep their onset times and drift with that exit instead of folding back across the groove.

`scene.py` builds the mesh only when `guide_rail` is present. The centerline is the marble path. Satin brass matches the hscroll divider `(0.62, 0.50, 0.30)` for the brackets and a brighter brass `(0.78, 0.62, 0.34)` for the channel.

```bash
cd tools/video/marble_music
python3 -m hscroll_descent.integrate \
  hscroll_descent/examples/jingle_remix_0_9_melody.hits.json \
  -o hscroll_descent/examples/guided_excerpt_plan.json \
  --seed 2 --launch-index 9
python3 -m hscroll_descent.diagram \
  hscroll_descent/examples/guided_excerpt_plan.json \
  hscroll_descent/examples/guided_excerpt_diagram.svg
python3 -m hscroll_descent.validate \
  hscroll_descent/examples/guided_excerpt_plan.json \
  -o hscroll_descent/examples/guided_excerpt_validation.json
```

Parent machine, low-resolution preview only. This VM does not run it:

```bash
blender -b --python tools/video/marble_music/scene.py -- \
  --plan tools/video/marble_music/hscroll_descent/examples/guided_excerpt_plan.json \
  --out /tmp/marble-guide-frames --res 960x540 --samples 4 --look v5
```

Checked on the guided plan with the existing strict scripts (full probe clouds, not every 8th sample):

```bash
python3 check_keepout.py hscroll_descent/examples/guided_excerpt_plan.json --look v5 --strict --sub 8
python3 check_pairs.py hscroll_descent/examples/guided_excerpt_plan.json --look v5 --strict
```

- `check_keepout.py` reports 0 violations. The closest non-hit approach is 1.03 R (0.155 m). Contact at the onset is about R (median 0.998 R).
- `check_pairs.py` reports 0 new clashes. The closest instruments are 6.1 cm apart.
- On the guide, distance to the inner floor is 0.150 m. That is the roll. Walls and brackets stay outside the marble and are not exempt.
- The groove lets go on a frame. The next rendered frame is 0.190 m from every channel sample, 40 mm outside the marble. Samples in the first few milliseconds are the tangent liftoff and do not penetrate.
- The only exemptions are a key's own onset (1.2 frames, the rule already in `check_keepout.py`) and floor contact while the phase is capture or rail.
- Descending layers share x, so the wall is one panel. Side-by-side families still get a divider. A reversed span used to lay two wall planes on top of each other; the brick shader on that overlap was the black-and-white triangle strip.
- The channel floor stays on one side of the marble. The old capture join flipped the normal and the connecting quad cut through the ball. Brackets leave from the outer rim, and a tapered lip does not leave a zero-area quad on the floor.
- A full triangle mesh was not run. `/workspace/marble/inst64/01_Jingle_Bells_64_Instruments_SingleStaff_Relay.mid`, Blender, `/workspace/om_pkg`, and the `.blend`/`.glb` caches are not here. Do not treat this remix excerpt as a certificate for that 64-instrument file.

## Limits

- Free strikes are point-mass frictionless impacts. Spin is modeled on the guide and then coasts. It does not push the center of mass.
- The groove is planar in XZ. The bank is a taller back wall, not a 3D lean into the wall.
- Free hops are also checked as capsule proxies. The strict gate for this excerpt is the full v5 probe clouds.
- `flute` v7/v8 and `frames_v5` are untouched.
