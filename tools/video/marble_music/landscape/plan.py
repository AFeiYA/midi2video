"""Find a gravity-driven marble route for the 16:9 Jingle Bells excerpt."""

import argparse
import json
from pathlib import Path

import numpy as np

from clearance import measure

DURATION = 10.0
GRAVITY = np.array([0.0, -9.81])
MARBLE_RADIUS = 0.09
PLATE_RADIUS = 0.027
CONTACT_DISTANCE = MARBLE_RADIUS + PLATE_RADIUS
PATH_MARGIN = 0.024
VIEWPORT = (-0.65, 15.35, -6.45, 2.55)
MAX_SPEED = 8.8

# Desired ball positions at selected zero-based hits. The solver is free to
# deviate from these anchors to preserve the timing and clearance constraints.
LAYOUTS = {
    "A": ("Long sweep", {
        0: (0.7, 1.5), 2: (2.15, 1.18), 4: (3.3, 0.72), 5: (4.45, 0.33),
        7: (5.25, -0.08), 9: (6.35, -0.72), 10: (8.82, -1.23), 14: (10.78, -2.12),
        15: (11.4, -2.77), 17: (12.0, -3.1), 21: (12.85, -4.18), 22: (14.2, -5.45),
    }),
    "B": ("Folded return", {
        0: (2.3, 1.5), 2: (4.0, 1.0), 4: (4.85, 0.38), 5: (3.68, -0.18),
        7: (2.12, -0.56), 9: (3.08, -1.22), 10: (6.55, -1.58), 14: (9.14, -2.63),
        15: (11.2, -3.35), 17: (12.18, -3.65), 21: (10.68, -4.52), 22: (13.35, -5.66),
    }),
    "C": ("Terraced descent", {
        0: (1.5, 1.58), 2: (3.11, 1.2), 4: (4.45, 0.9), 5: (6.55, -0.37),
        7: (6.25, -0.86), 9: (5.37, -1.33), 10: (8.0, -2.55), 14: (10.42, -2.77),
        15: (11.22, -3.05), 17: (11.92, -3.27), 20: (12.1, -3.72),
        21: (12.55, -4.22), 22: (13.98, -5.10),
    }),
}

ANGLES = np.linspace(0, 2 * np.pi, 80, endpoint=False)
NORMALS = np.tile(np.column_stack((np.cos(ANGLES), np.sin(ANGLES))), (5, 1))
RESTITUTION = np.repeat([0.50, 0.66, 0.79, 0.90, 0.97], len(ANGLES))


def axis_distance(samples, centers, directions, half_lengths):
    offsets = samples[:, None, :] - centers[None, :, :]
    along = np.sum(offsets * directions[None, :, :], axis=2)
    closest = along.clip(-half_lengths, half_lengths)
    return np.linalg.norm(offsets - closest[:, :, None] * directions, axis=2)


def inside(points):
    x0, x1, z0, z1 = VIEWPORT
    x, z = points.T
    return ((x > x0 + 0.21) & (x < x1 - 0.21) & (z > z0 + 0.21) & (z < z1 - 0.21)).all()


def clears_own_plate(points, strike, center, tangent, half_length):
    distances = axis_distance(
        points, center[None, :], tangent[None, :], np.array([half_length])
    )[:, 0]
    far_from_hit = np.linalg.norm(points - strike, axis=1) > 0.19
    return (
        (distances >= CONTACT_DISTANCE - 1e-6).all()
        and (distances[far_from_hit] >= CONTACT_DISTANCE + PATH_MARGIN).all()
    )


def solve(hits, layout, width=110):
    title, anchors = LAYOUTS[layout]
    times = np.array([hit["time"] for hit in hits] + [DURATION])
    if len(hits) != 23 or times[0] != 0 or (np.diff(times) <= 0).any():
        raise ValueError("These layout presets require 23 ordered hits starting at 0 s and ending before 10 s")

    indices = list(anchors)
    positions = np.array(list(anchors.values()))
    targets = np.column_stack([
        np.interp(times[:-1], times[indices], positions[:, axis]) for axis in (0, 1)
    ])
    half_lengths = np.array([
        0.205 if "Glockenspiel" in hit["track_name"] else 0.225 for hit in hits
    ])
    rng = np.random.default_rng(821)

    # Beam records hold the next strike and velocity, accepted strikes, sampled
    # travel history, and placed plate geometry.
    beam = []
    for vx in np.linspace(-0.1, 3.0, 11):
        for vz in (-3.2, -3.8, -4.4, -4.9):
            point = targets[0].copy()
            velocity = np.array([vx, vz])
            lead_in = np.linspace(-0.2, 0, 33)[:, None]
            trace = point + velocity * lead_in + 0.5 * GRAVITY * lead_in**2
            if inside(trace):
                beam.append((0.0, point, velocity, [], trace, np.empty((0, 2)), np.empty((0, 2))))

    for i, hit in enumerate(hits):
        dt = times[i + 1] - times[i]
        sample_t = np.linspace(0, dt, int(np.ceil(dt * 120)) + 1)[:, None]
        accel = 0.5 * GRAVITY * sample_t**2
        target_index = min(len(hits) - 1, i + 1)
        next_states = []
        for score, strike, incoming, history, trace, centers, axes in beam:
            incidence = NORMALS @ incoming
            outgoing = incoming - ((1 + RESTITUTION) * incidence)[:, None] * NORMALS
            end = strike + outgoing * dt + 0.5 * GRAVITY * dt * dt
            end_velocity = outgoing + GRAVITY * dt
            next_speed = np.linalg.norm(end_velocity, axis=1)
            delta = end - strike
            length = np.linalg.norm(delta, axis=1)
            good = (
                (incidence < -0.28)
                & (np.linalg.norm(outgoing - incoming, axis=1) > 0.67)
                & (next_speed <= MAX_SPEED)
            )
            if i + 1 < len(hits):
                good &= length > 0.28
            x0, x1, z0, z1 = VIEWPORT
            good &= ((end[:, 0] > x0 + 0.22) & (end[:, 0] < x1 - 0.22)
                     & (end[:, 1] > z0 + 0.22) & (end[:, 1] < z1 - 0.22))
            apex = strike[1] + np.maximum(outgoing[:, 1], 0)**2 / (2 * abs(GRAVITY[1]))
            good &= (apex < z1 + 0.9) | (outgoing[:, 1] > abs(GRAVITY[1]) * dt)
            if not good.any():
                continue

            if i + 1 < len(hits):
                cost = 1.9 * np.sum((end - targets[target_index])**2, axis=1)
            else:
                cost = 0.35 * np.sum((end - strike)**2, axis=1)
            cost += 0.06 * (np.linalg.norm(outgoing, axis=1) - 2.85)**2
            cost += 0.05 * (RESTITUTION - 0.80)**2
            if i + 2 < len(times) and times[i + 2] - times[i + 1] > 0.8:
                future_dt = times[i + 2] - times[i + 1]
                future_v = (targets[target_index + 1] - end - 0.5 * GRAVITY * future_dt**2) / future_dt
                needed_speed = np.linalg.norm(future_v, axis=1)
                cost += 2.0 * np.maximum(0, needed_speed - next_speed * 0.92)**2
            if history:
                last_delta = strike - np.array(history[-1]["p"])
                cosine = (delta @ last_delta) / np.maximum(1e-8, length * np.linalg.norm(last_delta))
                same_length = np.exp(-abs(length - np.linalg.norm(last_delta)) / 0.4)
                cost += 0.14 * np.maximum(cosine, 0)**2 * same_length
            if len(history) > 1:
                prior_delta = np.array(history[-1]["p"]) - np.array(history[-2]["p"])
                if np.sign(last_delta[0]) != np.sign(prior_delta[0]):
                    cost += 0.15 * (np.sign(last_delta[0]) != np.sign(delta[:, 0]))
            cost += 0.17 * np.maximum(0, apex - (z1 - 0.65))**2
            cost += rng.normal(0, 0.026, len(NORMALS))

            order = np.flatnonzero(good)
            accepted = 0
            for j in order[np.argsort(cost[order])][:66]:
                normal, velocity = NORMALS[j], outgoing[j]
                center = strike - normal * CONTACT_DISTANCE
                tangent = np.array([-normal[1], normal[0]])
                flight = strike + sample_t * velocity + accel
                if not inside(flight):
                    continue
                if len(centers):
                    near = np.linalg.norm(centers - center, axis=1) < 0.65
                    if near.any():
                        plate_axis = center + np.linspace(-half_lengths[i], half_lengths[i], 11)[:, None] * tangent
                        gaps = axis_distance(plate_axis, centers[near], axes[near], half_lengths[:i][near])
                        if gaps.min() < 2 * PLATE_RADIUS + 0.047:
                            continue
                    low, high = flight.min(axis=0) - 0.38, flight.max(axis=0) + 0.38
                    near = np.all((centers > low) & (centers < high), axis=1)
                    if near.any():
                        gaps = axis_distance(flight, centers[near], axes[near], half_lengths[:i][near])
                        if gaps.min() < CONTACT_DISTANCE + PATH_MARGIN:
                            continue
                # An instrument already exists during all earlier flights.
                past = trace[np.max(np.abs(trace - center), axis=1) < 0.40]
                if not clears_own_plate(past, strike, center, tangent, half_lengths[i]):
                    continue
                if not clears_own_plate(flight, strike, center, tangent, half_lengths[i]):
                    continue

                struck = dict(
                    hit=i + 1, time=float(times[i]), note=hit["note"], track=hit["track_name"],
                    p=strike.tolist(), plate_center=center.tolist(), normal=normal.tolist(),
                    half_length=float(half_lengths[i]), vin=incoming.tolist(), vout=velocity.tolist(),
                    restitution=float(RESTITUTION[j]), next_time=float(times[i + 1]),
                )
                next_states.append((
                    score + float(cost[j]), end[j], end_velocity[j], [*history, struck],
                    np.concatenate((trace, flight[1:])), np.vstack((centers, center)),
                    np.vstack((axes, tangent)),
                ))
                accepted += 1
                if accepted == 7:
                    break

        buckets = {}
        beam = []
        for state in sorted(next_states, key=lambda row: row[0]):
            _, point, velocity, *_ = state
            bucket = tuple(np.round(np.r_[point / [0.22, 0.17], velocity / [0.75, 0.75]]).astype(int))
            if buckets.get(bucket, 0) >= 2:
                continue
            buckets[bucket] = buckets.get(bucket, 0) + 1
            beam.append(state)
            if len(beam) >= width:
                break
        if not beam:
            raise RuntimeError(f"Layout {layout} ran out of candidates at hit {i + 1} ({times[i]:.3f} s)")

    strikes = beam[0][3]
    diagnostics, entry = measure(strikes, GRAVITY, MARBLE_RADIUS, PLATE_RADIUS)
    if (diagnostics["unintended_clearance_m"] <= 0 or diagnostics["board_clearance_m"] <= 0
            or diagnostics["max_contact_penetration_m"] > 1e-6
            or diagnostics["max_continuity_error_m"] > 1e-6
            or diagnostics["max_speed_squared_change_at_impact"] > 1e-6):
        raise RuntimeError(f"Layout {layout} failed continuous clearance or bounce checks: {diagnostics}")
    return dict(id=layout, title=title, hits=strikes, anchors=anchors, diagnostics=diagnostics, entry=entry)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("hits", type=Path, help="JSON from extract_hits.py for the first 10 seconds")
    parser.add_argument("--layout", choices=(*LAYOUTS, "all"), default="C")
    parser.add_argument("--beam-width", type=int, default=110)
    parser.add_argument("-o", "--output", type=Path, required=True)
    args = parser.parse_args()
    if args.beam_width < 1:
        parser.error("--beam-width must be positive")

    source = json.loads(args.hits.read_text(encoding="utf-8"))
    hits = [hit for hit in source["hits"] if hit["time"] < DURATION]
    layouts = LAYOUTS if args.layout == "all" else (args.layout,)
    plan = dict(
        source_midi=Path(source.get("midi", args.hits)).name,
        duration_s=DURATION, space="fixed orthographic XZ projection",
        viewport_xz_m=VIEWPORT, gravity_m_s2=GRAVITY.tolist(),
        marble_radius_m=MARBLE_RADIUS, plate_capsule_radius_m=PLATE_RADIUS,
        candidates=[solve(hits, layout, args.beam_width) for layout in layouts],
    )
    args.output.write_text(json.dumps(plan, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    for candidate in plan["candidates"]:
        report = candidate["diagnostics"]
        print(f"{candidate['id']}: {len(candidate['hits'])} hits, "
              f"ball clearance {report['unintended_clearance_m'] * 1000:.1f} mm, "
              f"plate clearance {report['board_clearance_m'] * 1000:.1f} mm")


if __name__ == "__main__":
    main()
