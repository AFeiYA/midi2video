"""Measure continuous XZ clearance against capsule proxies for the plates."""

from itertools import combinations

import numpy as np
from numpy.polynomial import Polynomial


def arc_clearance(arc, plate, duration, gravity, contact_distance):
    offset = np.array(arc["p"]) - np.array(plate["plate_center"])
    normal = np.array(plate["normal"])
    tangent = np.array([-normal[1], normal[0]])
    half = plate["half_length"]
    coefficients = np.array([offset, arc["vout"], 0.5 * gravity])
    along = Polynomial(coefficients @ tangent)
    across = Polynomial(coefficients @ normal)

    # The nearest point switches from the plate axis to an endpoint at ±half.
    # Test those switches, the stationary distances in each region, and both
    # ends of the arc. This includes minima between render frames.
    left = (along - half)**2 + across**2
    right = (along + half)**2 + across**2
    moments = [0.0, duration]
    for poly in (along - half, along + half, across, across.deriv(), left.deriv(), right.deriv()):
        moments.extend(
            float(root.real) for root in poly.roots()
            if abs(root.imag) < 1e-8 and 0 < root.real < duration
        )
    t = np.array(moments)
    distances = np.hypot(along(t) - np.clip(along(t), -half, half), across(t))
    return float(distances.min() - contact_distance)


def plate_axis(plate):
    nx, nz = plate["normal"]
    center = np.array(plate["plate_center"])
    extension = np.array([-nz, nx]) * plate["half_length"]
    return center - extension, center + extension


def endpoint_distance(point, start, end):
    axis = end - start
    fraction = np.clip((point - start) @ axis / (axis @ axis), 0, 1)
    return np.linalg.norm(point - start - fraction * axis)


def plate_clearance(a, b, radius):
    a0, a1 = plate_axis(a)
    b0, b1 = plate_axis(b)
    matrix = np.column_stack((a1 - a0, b0 - b1))
    if abs(np.linalg.det(matrix)) > 1e-10:
        t, u = np.linalg.solve(matrix, b0 - a0)
        if 0 <= t <= 1 and 0 <= u <= 1:
            return -2 * radius
    return float(min(
        endpoint_distance(a0, b0, b1), endpoint_distance(a1, b0, b1),
        endpoint_distance(b0, a0, a1), endpoint_distance(b1, a0, a1),
    ) - 2 * radius)


def measure(plates, gravity, marble_radius, plate_radius):
    first = plates[0]
    t = -0.2
    entry = dict(
        p=(np.array(first["p"]) + t * np.array(first["vin"]) + 0.5 * gravity * t**2).tolist(),
        vout=(np.array(first["vin"]) + gravity * t).tolist(),
        time=t, next_time=0,
    )
    arcs = [entry, *plates]
    clearance = np.inf
    penetration = continuity = top_speed = 0.0
    max_speed_gain = -np.inf
    reversals = direction = 0
    for i, arc in enumerate(arcs):
        dt = arc["next_time"] - arc["time"]
        velocity = np.array(arc["vout"])
        top_speed = max(top_speed, np.linalg.norm(velocity), np.linalg.norm(velocity + gravity * dt))
        if i < len(plates):
            end = np.array(arc["p"]) + velocity * dt + 0.5 * gravity * dt**2
            continuity = max(continuity, np.linalg.norm(end - plates[i]["p"]))
        if i:
            incoming = np.array(arc["vin"])
            max_speed_gain = max(max_speed_gain, velocity @ velocity - incoming @ incoming)
            dx = velocity[0] * dt
            if i < len(arcs) - 1 and abs(dx) >= 0.16:
                next_direction = 1 if dx > 0 else -1
                reversals += int(direction != 0 and direction != next_direction)
                direction = next_direction
        for j, plate in enumerate(plates):
            gap = arc_clearance(arc, plate, dt, gravity, marble_radius + plate_radius)
            # Arc i ends at plate i and (except the lead-in) starts at plate i-1.
            if j in (i, i - 1):
                penetration = max(penetration, -gap)
            else:
                clearance = min(clearance, gap)

    return dict(
        unintended_clearance_m=float(clearance),
        board_clearance_m=min(plate_clearance(a, b, plate_radius) for a, b in combinations(plates, 2)),
        max_contact_penetration_m=float(penetration),
        max_continuity_error_m=float(continuity),
        peak_speed_m_s=float(top_speed),
        horizontal_reversals=reversals,
        max_speed_squared_change_at_impact=float(max_speed_gain),
    ), entry
