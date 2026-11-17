"""One passive guide between two free strikes. Not a rollercoaster, and not rendered.

The marble already has velocity. Gravity speeds it up while it falls. A captive
circular groove then redirects that momentum leftward, through a valley and up
an exit lip, and lets go on the tangent. The lip is a local rise paid for by
kinetic energy plus the drop; it is not a motor and not a spring.

Two different forces:

- Capture slip is kinetic friction over a finite distance. Translation and
  spin change continuously until v = ω R. Friction does negative work.
- On the groove, the normal is a constraint force. Static friction keeps
  no-slip. Both do no work while the contact point is instantaneously at rest,
  so translational plus rotational plus potential energy stays constant.
  Height may rise and fall. Speed follows that budget.

A spring kicker is not implemented. Raising the exit speed above this budget
is reported as energy injection, not as a passive rail.

The scene builder reads ``guide_rail`` and sweeps this centerline into a
satin-brass channel with a taller outer wall through the turn and an open
lip. Portrait, v1, v2, and landscape plans do not carry that block.
"""

import argparse
import json
import math

import numpy as np

G = 9.81
K_SPIN = 2.0 / 5.0          # solid sphere, I / (m R^2)
MARBLE_RADIUS = 0.15
MU_KINETIC = 0.85           # slipping capture only; higher grip shortens the slide, it does not add energy
MU_STATIC_NOTE = 0.45       # reported against the required rolling friction; not a motor


def _flight(p, v, t, g):
    a = np.array([0.0, -g])
    p = np.asarray(p, float)
    v = np.asarray(v, float)
    return p + v * t + 0.5 * a * t * t, v + a * t


def _pose(center, radius, phi):
    center = np.asarray(center, float)
    point = center + radius * np.array([-math.sin(phi), math.cos(phi)])
    tangent = np.array([math.cos(phi), math.sin(phi)])
    return point, tangent


def _energy_flight(v, z, omega, radius, g):
    v = np.asarray(v, float)
    return 0.5 * float(v @ v) + 0.5 * K_SPIN * (omega * radius) ** 2 + g * float(z)


def _energy_roll(speed, z, g):
    return 0.5 * (1.0 + K_SPIN) * speed * speed + g * float(z)


def slide_to_rolling(velocity, omega, radius, g, mu=MU_KINETIC):
    """Finite-time kinetic-friction capture. Speed and spin stay continuous.

    The free flight may arrive with little spin. Friction opposes the slip
    u - ω R until they match. The end state is the no-slip speed fixed by
    angular momentum about the contact, so the result is a loss, not a kick.
    """
    velocity = np.asarray(velocity, float)
    speed = float(np.linalg.norm(velocity))
    if speed < 1e-6:
        return None
    tangent = velocity / speed
    u0 = speed
    w0 = float(omega)
    slip0 = u0 - w0 * radius
    if slip0 <= 1e-4:
        u_star, t_star = u0, 0.0
    else:
        accel = mu * g
        t_star = slip0 / (accel * (1.0 + 1.0 / K_SPIN))
        u_star = u0 - accel * t_star
    if u_star <= 0.15:
        return None
    steps = max(2, int(t_star / 0.002) + 1)
    path = []
    distance = 0.0
    prev_u = u0
    for i in range(steps + 1):
        frac = i / steps
        uu = u0 + (u_star - u0) * frac
        ww = w0 + (u_star / radius - w0) * frac
        if i:
            distance += 0.5 * (prev_u + uu) * (t_star / steps)
        path.append(dict(
            t=t_star * frac, distance=distance, speed=float(uu), omega=float(ww),
            energy=0.5 * uu * uu + 0.5 * K_SPIN * (ww * radius) ** 2,
        ))
        prev_u = uu
    return dict(
        tangent=tangent.tolist(), duration_s=float(t_star), distance_m=float(distance),
        speed_in=u0, speed_out=float(u_star), omega_in=w0, omega_out=float(u_star / radius),
        energy_in=path[0]["energy"], energy_out=path[-1]["energy"],
        energy_loss=path[0]["energy"] - path[-1]["energy"],
        samples=path, mu_kinetic=mu,
        force="kinetic_friction_over_a_finite_slip",
        discontinuous_velocity=False,
    )


def roll_circle(center, radius, phi0, phi1, speed0, g):
    """Clockwise captive groove. phi1 < phi0. Energy of rolling is constant."""
    if phi1 >= phi0:
        raise ValueError("clockwise rail requires phi1 < phi0")
    p0, _ = _pose(center, radius, phi0)
    budget = _energy_roll(speed0, p0[1], g)
    count = max(90, int(abs(phi1 - phi0) * radius / 0.008))
    phis = np.linspace(phi0, phi1, count)
    samples = []
    total_t = 0.0
    prev = None
    for phi in phis:
        point, tangent = _pose(center, radius, float(phi))
        available = budget - g * float(point[1])
        if available < -1e-8:
            return None, dict(
                status="cannot_crest_lip",
                z_m=float(point[1]),
                energy_budget=budget,
                energy_deficit_j_per_kg=float(-available),
                powered_kicker=False,
                message="The exit lip is above the rolling energy. The ball would stop and roll back. No spring is added.",
            )
        speed = math.sqrt(max(0.0, 2.0 * available / (1.0 + K_SPIN)))
        if prev is not None:
            ds = radius * abs(float(phi) - prev[0])
            denom = 0.5 * (speed + prev[1])
            if denom < 1e-4:
                return None, dict(status="stall", powered_kicker=False,
                                  message="Speed fell to zero on the rail. No kicker was applied.")
            total_t += ds / denom
        inward = center - point
        inward = inward / np.linalg.norm(inward)
        # m a = N + m g_vec, a = (v^2/R) toward the center.
        gvec = np.array([0.0, -g])
        constraint = (speed * speed / radius) * inward - gvec
        # Tangential gravity is balanced by static friction while rolling.
        tangent_up = np.array([-tangent[1], tangent[0]])
        # Required friction acceleration along the tangent is the tangential weight, scaled by k/(1+k).
        weight_tangent = -gvec @ tangent
        friction_accel = (K_SPIN / (1.0 + K_SPIN)) * weight_tangent
        samples.append(dict(
            phi=float(phi), p=[float(point[0]), float(point[1])],
            tangent=[float(tangent[0]), float(tangent[1])],
            speed=speed, t=total_t, z=float(point[1]),
            energy=_energy_roll(speed, point[1], g),
            constraint_accel_m_s2=[float(constraint[0]), float(constraint[1])],
            static_friction_accel_m_s2=float(friction_accel),
        ))
        prev = (float(phi), speed)
    zvals = [row["z"] for row in samples]
    return dict(samples=samples, duration_s=total_t, speed_exit=samples[-1]["speed"],
                p_exit=samples[-1]["p"], tangent_exit=samples[-1]["tangent"],
                z_entry=samples[0]["z"], z_exit=samples[-1]["z"], z_valley=min(zvals),
                energy=budget), None


def audit_transition(result, tol=1e-3):
    """Reject a tampered exit speed or a rising mechanical-energy budget."""
    violations = []
    if result.get("powered_kicker"):
        violations.append(dict(kind="energy", reason="powered_kicker"))
    phases = result.get("phases", [])
    previous = None
    for phase in phases:
        kind = phase["kind"]
        if kind == "free_flight":
            p0 = np.array(phase["p0"])
            v0 = np.array(phase["v0"])
            omega = phase["omega"]
            e0 = _energy_flight(v0, p0[1], omega, result["marble_radius_m"], result["g"])
            for sample in phase["samples"]:
                e = _energy_flight(sample["v"], sample["p"][1], omega, result["marble_radius_m"], result["g"])
                if e > e0 + tol:
                    violations.append(dict(kind="energy", reason="flight_gain", phase=phase["name"], gain=e - e0))
                    break
        elif kind == "slip_capture":
            energies = [row["energy"] for row in phase["samples"]]
            if energies[-1] > energies[0] + tol:
                violations.append(dict(kind="energy", reason="capture_gain"))
            speeds = [row["speed"] for row in phase["samples"]]
            if max(abs(speeds[i + 1] - speeds[i]) for i in range(len(speeds) - 1)) > 1.5:
                # A single sample step of the continuous ramp should be small.
                violations.append(dict(kind="continuity", reason="capture_speed_jump"))
        elif kind == "rolling_rail":
            energies = [row["energy"] for row in phase["samples"]]
            if max(energies) > min(energies) + tol + 1e-3:
                # constant within integration error
                if max(energies) - energies[0] > tol:
                    violations.append(dict(kind="energy", reason="rail_gain", gain=max(energies) - energies[0]))
            v_exit = np.array(phase["v_exit"])
            tangent = np.array(phase["tangent_exit"])
            cross = v_exit[0] * tangent[1] - v_exit[1] * tangent[0]
            speed = float(np.linalg.norm(v_exit))
            sample_speed = float(phase["samples"][-1]["speed"])
            if speed > sample_speed + 1e-3:
                violations.append(dict(kind="energy", reason="energy_injection", gain=0.5 * (speed ** 2 - sample_speed ** 2)))
            if float(v_exit @ tangent) <= 0 or abs(cross) > 1e-4 * (speed + 1e-9):
                violations.append(dict(kind="continuity", reason="exit_not_tangent"))
        if previous is not None:
            if np.linalg.norm(np.array(previous["p_end"]) - np.array(phase["p0"])) > 1e-5:
                violations.append(dict(kind="continuity", reason="position_gap", at=phase["name"]))
            if np.linalg.norm(np.array(previous["v_end"]) - np.array(phase["v0"])) > 1e-4:
                violations.append(dict(kind="continuity", reason="velocity_gap", at=phase["name"]))
        previous = phase
    return dict(ok=not violations, violations=violations)


def _release_target(t_release, t0, fps):
    """Frame time at or just before ``t_release``, as a release clock.

    The release has to land on that frame or up to 0.4 ms after it. A release
    a fraction of a frame early would put a rendered frame in the 1 mm liftoff.
    """
    absolute = float(t0) + float(t_release)
    frame = math.floor(absolute * fps + 1e-9) / fps
    return frame - float(t0)


def _snap_phi(center, radius, heading, speed, g, phi_hint, t_fall, slide_dur, dt, t0, fps):
    """Move the lip angle so the groove lets go on a rendered frame."""
    def duration(phi1):
        rolled, fail = roll_circle(center, radius, heading, phi1, speed, g)
        if fail is not None or rolled is None:
            return None, None
        return rolled["duration_s"], rolled

    hint_dur, hint_roll = duration(phi_hint)
    if hint_roll is None:
        return None
    target = _release_target(t_fall + slide_dur + hint_dur, t0, fps)
    # Shorter rail: phi closer to heading. Longer rail: phi more negative.
    lo, hi = phi_hint - 0.45, min(heading - 0.04, phi_hint + 0.45)
    best = None
    for _ in range(18):
        mid = 0.5 * (lo + hi)
        dur, rolled = duration(mid)
        if rolled is None:
            hi = mid
            continue
        release = t_fall + slide_dur + dur
        err = release - target
        best = (rolled, release, mid)
        if abs(err) <= 4e-4 and err >= -1e-4:
            return rolled, release
        if release > target:
            lo = mid
        else:
            hi = mid
    if best is None:
        return None
    rolled, release, _mid = best
    if abs(release - target) > 1.5e-3 or release + 1e-4 < target:
        # One frame later, still on a frame, if the shorter lip will not sit.
        target2 = target + 1.0 / fps
        lo, hi = phi_hint - 0.55, min(heading - 0.04, phi_hint + 0.2)
        for _ in range(18):
            mid = 0.5 * (lo + hi)
            dur, rolled = duration(mid)
            if rolled is None:
                hi = mid
                continue
            release = t_fall + slide_dur + dur
            if abs(release - target2) <= 4e-4 and release + 1e-4 >= target2:
                return rolled, release
            if release > target2:
                lo = mid
            else:
                hi = mid
    return None


def plan_guided_hop(v0, dt, g=G, omega0=0.0, p0=(0.0, 0.0), mu=MU_KINETIC, t0=None, fps=None, accept=None):
    """Fall, slip into a roll, ride a descending U with an exit lip, then fly.

    ``dt`` is the musical gap. The landing position is wherever that budget
    reaches; it is not snapped to a pre-drawn coordinate. Returns status ok
    or a refusal that does not raise the exit speed.
    """
    p0 = np.asarray(p0, float)
    v0 = np.asarray(v0, float)
    if float(np.linalg.norm(v0)) < 0.4:
        return dict(status="refused", powered_kicker=False,
                    message="This rail does not start a resting ball. It needs the incoming velocity.")
    best = None
    refusals = []
    for t_fall in np.linspace(0.28, 0.62, 8):
        p_cap, v_cap = _flight(p0, v0, float(t_fall), g)
        if float(v_cap[1]) > -0.15 or float(v_cap[0]) < 0.2:
            continue
        heading = math.atan2(float(v_cap[1]), float(v_cap[0]))
        slide = slide_to_rolling(v_cap, omega0, MARBLE_RADIUS, g, mu=mu)
        if slide is None or slide["duration_s"] <= 0.0:
            continue
        slide_vec = slide["speed_out"] * np.array(slide["tangent"])
        p_rail = p_cap + np.array(slide["tangent"]) * slide["distance_m"]
        for radius in (0.32, 0.42, 0.55):
            center = p_rail - radius * np.array([-math.sin(heading), math.cos(heading)])
            for extra in (0.12, 0.22, 0.38, 0.55):
                phi1 = -math.pi - extra
                if phi1 >= heading:
                    continue
                rolled, fail = roll_circle(center, radius, heading, phi1, slide["speed_out"], g)
                if fail is not None:
                    refusals.append(fail)
                    continue
                if t0 is not None and fps:
                    snapped = _snap_phi(
                        center, radius, heading, slide["speed_out"], g, phi1,
                        float(t_fall), slide["duration_s"], dt, t0, fps,
                    )
                    if snapped is None:
                        continue
                    rolled, _release = snapped
                t_left = dt - t_fall - slide["duration_s"] - rolled["duration_s"]
                if t_left < 0.20:
                    continue
                v_exit = rolled["speed_exit"] * np.array(rolled["tangent_exit"])
                if float(v_exit[0]) > -0.15:
                    continue
                p_land, v_land = _flight(rolled["p_exit"], v_exit, t_left, g)
                if float(v_land[1]) > -0.2:
                    continue
                if float(p_land[1]) > float(p0[1]) - 0.15:
                    continue
                below = rolled["z_valley"] - float(p_land[1])
                lip = rolled["z_exit"] - rolled["z_valley"]
                if lip < 0.05:
                    continue
                # Prefer a clearly visible fall, reversal, and lip.
                score = abs(t_left - 0.48) + 0.5 * max(0.0, 0.6 - below)
                packed = (score, t_fall, slide, rolled, p_cap, v_cap, p_rail, v_exit, p_land, v_land, t_left, radius, heading, center)
                if accept is not None and not accept(packed):
                    continue
                if best is None or score < best[0]:
                    best = packed
    if best is None:
        return dict(
            status="refused", powered_kicker=False, energy_was_relaxed=False,
            message="No captive rail in the searched family lands a falling, leftward, lower strike inside this musical gap. Exit speed was not increased.",
            lip_refusals=len(refusals),
        )
    _, t_fall, slide, rolled, p_cap, v_cap, p_rail, v_exit, p_land, v_land, t_left, radius, heading, center = best
    result = materialize_guide(
        p0, v0, g, dt, omega0, mu, t_fall, slide, rolled, p_cap, v_cap, v_exit, t_left, radius, center,
    )
    result["audit"] = audit_transition(result)
    if not result["audit"]["ok"]:
        result["status"] = "audit_failed"
    return result


def materialize_guide(p0, v0, g, dt, omega0, mu, t_fall, slide, rolled, p_cap, v_cap, v_exit, t_left, radius, center):
    """Build the phase dict for one already-accepted geometry."""
    # Rebuild the free-flight samples for the audit and the diagram.
    def flight_phase(name, p, v, duration, omega):
        count = max(12, int(duration / 0.02))
        rows = []
        for i in range(count + 1):
            tt = duration * i / count
            point, vel = _flight(p, v, tt, g)
            rows.append(dict(t=tt, p=[float(point[0]), float(point[1])], v=[float(vel[0]), float(vel[1])],
                             speed=float(np.linalg.norm(vel))))
        return dict(kind="free_flight", name=name, p0=[float(p[0]), float(p[1])], v0=[float(v[0]), float(v[1])],
                    omega=omega, duration_s=duration, samples=rows,
                    p_end=rows[-1]["p"], v_end=rows[-1]["v"])

    fall = flight_phase("fall", p0, v0, t_fall, omega0)
    # Slide occupies distance along the capture tangent, starting at p_cap.
    slide_samples = []
    for row in slide["samples"]:
        point = p_cap + np.array(slide["tangent"]) * row["distance"]
        vel = row["speed"] * np.array(slide["tangent"])
        slide_samples.append(dict(t=row["t"], distance=row["distance"], speed=row["speed"], omega=row["omega"],
                                  energy=row["energy"] + g * float(point[1]),
                                  p=[float(point[0]), float(point[1])], v=[float(vel[0]), float(vel[1])]))
    slip = dict(
        kind="slip_capture", name="capture",
        p0=fall["p_end"], v0=fall["v_end"],
        p_end=slide_samples[-1]["p"], v_end=slide_samples[-1]["v"],
        samples=slide_samples, duration_s=slide["duration_s"],
        energy_loss_j_per_kg=slide["energy_loss"],
        force=slide["force"], mu_kinetic=mu,
        note="Kinetic friction during slip. Not the rail's later constraint force.",
    )
    rail_samples = []
    for row in rolled["samples"]:
        vel = row["speed"] * np.array(row["tangent"])
        rail_samples.append(dict(**row, v=[float(vel[0]), float(vel[1])]))
    rail = dict(
        kind="rolling_rail", name="rail",
        p0=slip["p_end"], v0=slip["v_end"],
        p_end=rolled["p_exit"], v_exit=[float(v_exit[0]), float(v_exit[1])],
        v_end=[float(v_exit[0]), float(v_exit[1])],
        tangent_exit=rolled["tangent_exit"],
        samples=rail_samples, duration_s=rolled["duration_s"],
        z_entry=rolled["z_entry"], z_valley=rolled["z_valley"], z_exit=rolled["z_exit"],
        radius_m=radius, center=[float(center[0]), float(center[1])],
        force="constraint_normal_and_static_friction",
        work_j_per_kg=0.0,
        model="rolling_without_slip_solid_sphere",
        k_spin=K_SPIN,
        note="While the contact point is instantaneously at rest, normal and static friction do no work. Local upslope is allowed.",
    )
    launch = flight_phase("exit_flight", rolled["p_exit"], v_exit, t_left, slide["omega_out"])
    result = dict(
        status="ok",
        renderer_supported=False,
        powered_kicker=False,
        energy_was_relaxed=False,
        g=g,
        dt_s=dt,
        marble_radius_m=MARBLE_RADIUS,
        assumption="Incoming spin is zero after the free strike. Capture uses kinetic friction until v = ω R, continuously. The groove then enforces rolling.",
        phases=[fall, slip, rail, launch],
        landing=dict(p=launch["p_end"], v=launch["v_end"], t=dt,
                     note="Next musical contact. Position is the passive landing, not a coordinate copied from the free-flight plan."),
        speed_at_launch=fall["samples"][0]["speed"],
        speed_at_capture=float(np.linalg.norm(v_cap)),
        exit_heading="leftward",
        references=[
            "OpenStax University Physics Volume 1, §11.1: rolling KE and why static friction does no work.",
            "Pinball habitrails are passive wire guides. A vertical up-kicker is a powered device and is not this transition.",
        ],
    )
    return result


def static_deflector(vin, normal, restitution):
    """One passive impact. Restitution above 1 is a spring and is refused."""
    from hscroll_descent.physics import classify_bounce, reflect
    normal = np.asarray(normal, float)
    normal = normal / np.linalg.norm(normal)
    vout = reflect(vin, normal, restitution)
    verdict = classify_bounce(vin, vout, normal)
    return dict(
        kind="impact_impulse",
        ok=bool(verdict["ok"]),
        powered_kicker=verdict.get("reason") == "energy_injection",
        energy_gain=verdict.get("energy_gain"),
        vout=np.asarray(vout, float).tolist(),
        note="A static plate redirects momentum with an impulse. It is not the rail constraint, and it is not a spring.",
    )


def refusal_if_lip_too_high(g=G):
    """A lip above the rolling budget stops the ball. It does not add a kicker."""
    center = np.array([0.0, 1.0])
    _rolled, fail = roll_circle(center, 0.8, -math.pi, -math.pi - 2.2, 1.2, g)
    if fail is None:
        return dict(status="unexpected_success", powered_kicker=False)
    fail["powered_kicker"] = False
    return fail


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dt", type=float, default=1.22449, help="musical gap in seconds (jingle long note)")
    ap.add_argument("--g", type=float, default=G)
    ap.add_argument("-o", required=True)
    ap.add_argument("--svg", default="")
    args = ap.parse_args(argv)
    # Rightward and slightly upward: the strike has already happened. The fall
    # that follows is where gravity adds speed.
    result = plan_guided_hop(np.array([2.35, 0.85]), args.dt, g=args.g)
    with open(args.o, "w", encoding="utf-8") as handle:
        json.dump(result, handle)
        handle.write("\n")
    if args.svg and result["status"] == "ok":
        from hscroll_descent.diagram import write_rail_svg
        write_rail_svg(result, args.svg)
    print(result["status"], "renderer_supported", result.get("renderer_supported"),
          "powered_kicker", result.get("powered_kicker"))
    if result["status"] != "ok":
        print(result.get("message", result.get("audit")))
        raise SystemExit(2)


if __name__ == "__main__":
    main()
