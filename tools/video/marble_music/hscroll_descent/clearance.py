"""Continuous capsule-proxy clearance in the XZ plane.

Each contact plate is a capsule: a segment of the given half-length thickened
by the plate radius. The marble is a circle of ``marble_radius``. This is a
proxy for the contact bar, not the decorative instrument mesh. A capsule of
radius equal to the plate half-thickness contains the rectangular contact bar,
so a positive capsule gap is a positive bar gap. Parts that stick out past
that bar (bowls, necks, resonators, pins) are outside this check.

The gap along a flight is the minimum of a dense sample and the critical
points of the squared distance to the segment (the same root set used for a
quadratic-under-gravity trajectory: endpoints, the along-track joins at
±half-length, and stationary points of the distance). Minima between frames
are included.
"""

import numpy as np
from numpy.polynomial import Polynomial


def _segment(center, normal, half):
    tangent = np.array([-normal[1], normal[0]], dtype=float)
    center = np.asarray(center, dtype=float)
    return center - tangent * half, center + tangent * half


def segment_distance(a, b, c, d):
    """Minimum distance between segments ab and cd in 2D."""
    a, b, c, d = map(lambda p: np.asarray(p, dtype=float), (a, b, c, d))

    def point_segment(p, s, e):
        ab = e - s
        denom = float(ab @ ab)
        if denom < 1e-18:
            return float(np.linalg.norm(p - s))
        t = float(np.clip((p - s) @ ab / denom, 0.0, 1.0))
        return float(np.linalg.norm(p - (s + t * ab)))

    best = min(point_segment(a, c, d), point_segment(b, c, d),
               point_segment(c, a, b), point_segment(d, a, b))
    ab, cd = b - a, d - c
    matrix = np.column_stack((ab, -cd))
    if abs(np.linalg.det(matrix)) > 1e-12:
        t, u = np.linalg.solve(matrix, c - a)
        if 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0:
            best = min(best, float(np.linalg.norm((a + t * ab) - (c + u * cd))))
    return best


def plate_plate_gap(a, b, plate_radius):
    a0, a1 = _segment(a["center"], a["normal"], a["half_length"])
    b0, b1 = _segment(b["center"], b["normal"], b["half_length"])
    return segment_distance(a0, a1, b0, b1) - 2.0 * plate_radius


def flight_plate_gap(p0, velocity, duration, gravity_vector, plate, marble_radius, samples=240):
    """Minimum (distance from marble centre to the capsule) minus contact distance.

    Negative means the circle intersects the capsule.
    """
    p0 = np.asarray(p0, dtype=float)
    velocity = np.asarray(velocity, dtype=float)
    gravity_vector = np.asarray(gravity_vector, dtype=float)
    normal = np.asarray(plate["normal"], dtype=float)
    center = np.asarray(plate["center"], dtype=float)
    half = float(plate["half_length"])
    tangent = np.array([-normal[1], normal[0]])
    radius_sum = float(marble_radius) + float(plate["radius"])
    offset = p0 - center
    coefficients = np.vstack([offset, velocity, 0.5 * gravity_vector])
    along = Polynomial(coefficients @ tangent)
    across = Polynomial(coefficients @ normal)
    left = (along - half) ** 2 + across ** 2
    right = (along + half) ** 2 + across ** 2
    moments = [0.0, float(duration)]
    for poly in (along - half, along + half, across, across.deriv(), left.deriv(), right.deriv()):
        for root in poly.roots():
            if abs(root.imag) < 1e-7 and 0.0 < float(root.real) < duration:
                moments.append(float(root.real))
    count = max(int(samples), 2)
    moments.extend(np.linspace(0.0, float(duration), count).tolist())
    ts = np.asarray(moments, dtype=float)
    along_v = along(ts)
    dist = np.hypot(along_v - np.clip(along_v, -half, half), across(ts))
    return float(dist.min() - radius_sum)


def sampled_flight_gap(p0, velocity, duration, g, plate, marble_radius, samples=96,
                       ignore_start=0.0, ignore_end=0.0):
    """Fast gap used while searching.

    ``ignore_start`` / ``ignore_end`` drop a short time margin at the contact
    that this flight is allowed to touch. The rest of the flight, including
    every sample between those margins, must stay clear.
    """
    duration = float(duration)
    n = max(int(samples), 8)
    t = np.linspace(0.0, duration, n)
    keep = np.ones(n, dtype=bool)
    if ignore_start > 0.0:
        keep &= t > ignore_start
    if ignore_end > 0.0:
        keep &= t < duration - ignore_end
    if int(keep.sum()) < 4:
        keep = np.ones(n, dtype=bool)
    t = t[keep]
    a = np.array([0.0, -float(g)])
    pts = np.asarray(p0, dtype=float) + np.asarray(velocity, dtype=float) * t[:, None] + 0.5 * a * (t ** 2)[:, None]
    normal = np.asarray(plate["normal"], dtype=float)
    tangent = np.array([-normal[1], normal[0]])
    rel = pts - np.asarray(plate["center"], dtype=float)
    along = rel @ tangent
    dist = np.hypot(along - np.clip(along, -plate["half_length"], plate["half_length"]), rel @ normal)
    return float(dist.min() - (marble_radius + plate["radius"]))
