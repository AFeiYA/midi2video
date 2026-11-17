"""Passive frictionless ballistics in the XZ plane.

z is up. Gravity is (0, -g). A fixed plate may remove mechanical energy at a
contact. It cannot add any. The only energy in the route is the marble's
entry state.

Specific mechanical energy, per unit mass::

    E = 0.5 * |v|^2 + g * z

Flight at constant gravity conserves E exactly. At a frictionless contact with
restitution e the normal is the direction of the impulse::

    n = (v_out - v_in) / |v_out - v_in|
    v_out = v_in - (1 + e) * (v_in · n) * n

Approach requires v_in · n < 0 and departure v_out · n > 0, with n pointing
into the free half-space. For that pair, 0 <= e <= 1 if and only if
|v_out| <= |v_in|. e > 1 is an energy injection and is rejected.
"""

import math

import numpy as np

G_DEFAULT = 9.81


def gravity_vector(g):
    return np.array([0.0, -float(g)])


def specific_energy(velocity, z, g):
    v = np.asarray(velocity, dtype=float)
    return 0.5 * float(v @ v) + float(g) * float(z)


def reflect(vin, normal, restitution):
    """Frictionless bounce. restitution may be above 1; callers must reject that."""
    n = np.asarray(normal, dtype=float)
    v = np.asarray(vin, dtype=float)
    return v - (1.0 + float(restitution)) * float(v @ n) * n


def flight_state(p0, v0, t, g):
    p0 = np.asarray(p0, dtype=float)
    v0 = np.asarray(v0, dtype=float)
    a = gravity_vector(g)
    tt = float(t)
    return p0 + v0 * tt + 0.5 * a * tt * tt, v0 + a * tt


def flight_apex_z(z, vz, duration, g):
    """Highest z on the closed interval [0, duration]."""
    z = float(z)
    vz = float(vz)
    duration = float(duration)
    if vz <= 0.0 or duration <= 0.0:
        return z
    t_apex = vz / float(g)
    if t_apex >= duration:
        end, _ = flight_state([0.0, z], [0.0, vz], duration, g)
        return float(end[1])
    return z + vz * vz / (2.0 * float(g))


def classify_bounce(vin, vout, normal=None, approach_min=0.30, depart_min=0.08):
    """Return a dict describing a frictionless passive bounce, or why it is not one.

    If ``normal`` is omitted, the only normal consistent with a frictionless
    impulse is used: the direction of ``vout - vin``.
    """
    vin = np.asarray(vin, dtype=float)
    vout = np.asarray(vout, dtype=float)
    delta = vout - vin
    delta_n = float(np.linalg.norm(delta))
    speed_in = float(np.linalg.norm(vin))
    speed_out = float(np.linalg.norm(vout))
    if delta_n < 1e-8:
        return dict(ok=False, reason="no_impulse", restitution=None, normal=None,
                    energy_gain=0.5 * (speed_out ** 2 - speed_in ** 2))
    implied = delta / delta_n
    if normal is None:
        normal = implied
    else:
        normal = np.asarray(normal, dtype=float)
        nn = float(np.linalg.norm(normal))
        if nn < 1e-12:
            return dict(ok=False, reason="degenerate_normal", restitution=None, normal=None,
                        energy_gain=0.5 * (speed_out ** 2 - speed_in ** 2))
        normal = normal / nn
        if float(normal @ implied) < 1.0 - 1e-6:
            # A frictionless plate can only push along its normal. A mismatch
            # means the velocity change is not a passive normal impulse.
            # Still report energy if the speed grew, so an injection is visible
            # even when the direction is also wrong.
            gain = 0.5 * (speed_out ** 2 - speed_in ** 2)
            reason = "energy_injection" if gain > 1e-8 else "impulse_not_along_normal"
            return dict(ok=False, reason=reason, restitution=None, normal=normal.tolist(),
                        energy_gain=gain, implied_normal=implied.tolist())
    approach = -float(vin @ normal)
    depart = float(vout @ normal)
    gain = 0.5 * (speed_out ** 2 - speed_in ** 2)
    if approach <= 1e-9:
        return dict(ok=False, reason="not_approaching", restitution=None, normal=normal.tolist(),
                    energy_gain=gain, approach=approach, depart=depart)
    restitution = delta_n / approach - 1.0
    if gain > 1e-8 or restitution > 1.0 + 1e-8:
        return dict(ok=False, reason="energy_injection", restitution=float(restitution),
                    normal=normal.tolist(), energy_gain=gain, approach=approach, depart=depart,
                    speed_in=speed_in, speed_out=speed_out)
    if restitution < -1e-8:
        return dict(ok=False, reason="negative_restitution", restitution=float(restitution),
                    normal=normal.tolist(), energy_gain=gain, approach=approach, depart=depart)
    if approach < approach_min:
        return dict(ok=False, reason="approach_too_glancing", restitution=float(restitution),
                    normal=normal.tolist(), energy_gain=gain, approach=approach, depart=depart)
    if depart < depart_min:
        return dict(ok=False, reason="does_not_leave_plate", restitution=float(restitution),
                    normal=normal.tolist(), energy_gain=gain, approach=approach, depart=depart)
    return dict(ok=True, reason="passive", restitution=float(restitution), normal=normal.tolist(),
                energy_gain=gain, approach=approach, depart=depart,
                speed_in=speed_in, speed_out=speed_out)


def mount_of(normal, tilt_deg):
    """'floor' if the free side is mostly up, 'ceil' if mostly down, else None."""
    nz = float(np.asarray(normal, dtype=float)[1])
    limit = math.cos(math.radians(tilt_deg))
    if nz >= limit:
        return "floor"
    if nz <= -limit:
        return "ceil"
    return None


def outgoing_grid(vin, mount, tilt_deg, restitutions):
    """Every frictionless bounce on the tilt cone. Each result is passive by construction."""
    vin = np.asarray(vin, dtype=float)
    tilt = math.radians(tilt_deg)
    angles = np.linspace(-tilt, tilt, 41)
    found = []
    for angle in angles:
        s, c = math.sin(angle), math.cos(angle)
        normal = np.array([s, c if mount == "floor" else -c])
        approach = -float(vin @ normal)
        if approach < 0.30:
            continue
        for e in restitutions:
            vout = reflect(vin, normal, e)
            if float(vout @ normal) < 0.08:
                continue
            if float(vout @ vout) > float(vin @ vin) + 1e-8:
                continue
            found.append((vout, normal, float(e), approach))
    return found


def release_from_arrival(contact, vin, pre, g):
    """Finite release state whose ballistic arrival is ``contact`` with velocity ``vin``."""
    contact = np.asarray(contact, dtype=float)
    vin = np.asarray(vin, dtype=float)
    pre = float(pre)
    a = gravity_vector(g)
    v_release = vin - a * pre
    p_release = contact - v_release * pre - 0.5 * a * pre * pre
    return p_release, v_release
