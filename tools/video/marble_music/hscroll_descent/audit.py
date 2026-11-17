"""Audit a descending-layer route.

Checks, each named in the report:

- timing: contact times equal the MIDI times; every frame and contact lies on
  the ballistic flight
- surface: frictionless normal, approach from the free side, departure into it,
  mount consistent with the tilt cone
- energy: specific energy does not increase at a contact and is constant in flight
- clearance: continuous capsule proxy (polynomial critical points plus samples)

These are proxy and excerpt checks. They are not a full triangle-mesh sweep,
not ``check_keepout.py`` / ``check_pairs.py``, and not a whole-song certificate.
"""

import numpy as np

from hscroll_descent.clearance import flight_plate_gap, plate_plate_gap
from hscroll_descent.physics import classify_bounce, flight_state, gravity_vector, mount_of, specific_energy


def _violation(kind, **detail):
    row = dict(kind=kind)
    row.update(detail)
    return row


def audit_route(route, clearance_margin=0.012, penetration_tol=2.5e-5, energy_tol=1e-7, time_tol=1e-8):
    g = float(route["g"])
    gvec = gravity_vector(g)
    contacts = route["contacts"]
    flights = route["flights"]
    plates = route["plates"]
    violations = []
    hit_times = [float(h["time"]) for h in route["hits"]]
    if len(hit_times) != len(contacts):
        violations.append(_violation("timing", reason="contact_count", hits=len(hit_times), contacts=len(contacts)))
    for c, t_hit in zip(contacts, hit_times):
        if abs(float(c["time"]) - t_hit) > time_tol:
            violations.append(_violation("timing", reason="contact_time", hit=c["i"],
                                         plan=c["time"], midi=t_hit))

    energies = []
    for c in contacts:
        verdict = classify_bounce(c["vin"], c["vout"], c["normal"])
        if not verdict["ok"]:
            violations.append(_violation("surface" if verdict["reason"] != "energy_injection" else "energy",
                                         reason=verdict["reason"], hit=c["i"],
                                         restitution=verdict.get("restitution"),
                                         energy_gain=verdict.get("energy_gain")))
        else:
            if verdict["energy_gain"] > energy_tol:
                violations.append(_violation("energy", reason="energy_injection", hit=c["i"],
                                             energy_gain=verdict["energy_gain"],
                                             restitution=verdict["restitution"]))
            mount = c["mount"]
            nz = float(c["normal"][1])
            cone = mount_of(c["normal"], route.get("tilt_deg", 60.0))
            if cone != mount:
                violations.append(_violation("surface", reason="normal_outside_mount_cone", hit=c["i"],
                                             mount=mount, cone=cone))
            if mount == "floor" and nz <= 0:
                violations.append(_violation("surface", reason="floor_normal_not_up", hit=c["i"]))
            if mount == "ceil" and nz >= 0:
                violations.append(_violation("surface", reason="ceil_normal_not_down", hit=c["i"]))
            vin_z = float(c["vin"][1])
            if mount == "floor" and vin_z >= -1e-6:
                violations.append(_violation("surface", reason="floor_arrival_not_falling", hit=c["i"], vin_z=vin_z))
            if mount == "ceil" and vin_z <= 1e-6:
                violations.append(_violation("surface", reason="ceil_arrival_not_rising", hit=c["i"], vin_z=vin_z))
        e_in = specific_energy(c["vin"], c["p"][1], g)
        e_out = specific_energy(c["vout"], c["p"][1], g)
        energies.append((e_in, e_out))
        if e_out > e_in + energy_tol:
            violations.append(_violation("energy", reason="energy_injection", hit=c["i"],
                                         energy_in=e_in, energy_out=e_out, energy_gain=e_out - e_in))

    # Flight conservation, continuity, and proxy clearance.
    min_clearance = np.inf
    max_penetration = 0.0
    per_flight_clearance = []
    for flight in flights:
        p0 = np.asarray(flight["p0"], dtype=float)
        v = np.asarray(flight["v"], dtype=float)
        dt = float(flight["t1"] - flight["t0"])
        end, vend = flight_state(p0, v, dt, g)
        e0 = specific_energy(v, p0[1], g)
        e1 = specific_energy(vend, end[1], g)
        if abs(e1 - e0) > 1e-6:
            violations.append(_violation("energy", reason="flight_energy_drift", flight=flight["role"],
                                         t0=flight["t0"], drift=e1 - e0))
        start_i = flight.get("start_contact")
        end_i = flight.get("end_contact")
        if start_i is not None:
            c = contacts[start_i]
            if np.linalg.norm(p0 - np.asarray(c["p"])) > 1e-6:
                violations.append(_violation("timing", reason="flight_start_gap", hit=start_i))
            if np.linalg.norm(v - np.asarray(c["vout"])) > 1e-6:
                violations.append(_violation("timing", reason="flight_velocity_gap", hit=start_i))
        if end_i is not None:
            c = contacts[end_i]
            if np.linalg.norm(end - np.asarray(c["p"])) > 1e-6:
                violations.append(_violation("timing", reason="flight_end_gap", hit=end_i,
                                             gap=float(np.linalg.norm(end - np.asarray(c["p"])))))
            if np.linalg.norm(vend - np.asarray(c["vin"])) > 1e-6:
                violations.append(_violation("timing", reason="arrival_velocity_gap", hit=end_i))
        flight_clear = np.inf
        for plate in plates:
            gap = flight_plate_gap(p0, v, dt, gvec, plate, route["marble_radius"])
            owns = plate["contact"] in (start_i, end_i)
            if owns:
                if -gap > max_penetration:
                    max_penetration = -gap
                if -gap > penetration_tol:
                    violations.append(_violation("clearance", reason="contact_plate_penetration",
                                                 flight=flight["role"], plate=plate["contact"],
                                                 t0=flight["t0"], penetration_m=float(-gap),
                                                 check="capsule_proxy"))
            else:
                flight_clear = min(flight_clear, gap)
                min_clearance = min(min_clearance, gap)
                if gap < clearance_margin:
                    violations.append(_violation("clearance", reason="proxy_intersection",
                                                 flight=flight["role"], plate=plate["contact"],
                                                 t0=flight["t0"], gap_m=float(gap),
                                                 check="capsule_proxy"))
        per_flight_clearance.append(None if flight_clear is np.inf else float(flight_clear))

    min_plate = np.inf
    for i in range(len(plates)):
        for j in range(i + 1, len(plates)):
            gap = plate_plate_gap(plates[i], plates[j], plates[i]["radius"])
            min_plate = min(min_plate, gap)
            if gap < clearance_margin:
                violations.append(_violation("clearance", reason="plates_overlap",
                                             a=plates[i]["contact"], b=plates[j]["contact"],
                                             gap_m=float(gap), check="capsule_proxy"))

    # Layer descent: no height reset. Contacts stay at or below the opening
    # contact, and each new layer opens below the previous layer's lowest contact.
    if contacts:
        z0 = float(contacts[0]["p"][1])
        if not route.get("entry", {}).get("resumed"):
            for c in contacts:
                if float(c["p"][1]) > z0 + 1e-6:
                    violations.append(_violation("layer", reason="contact_above_start", hit=c["i"], z=c["p"][1]))
        layers = {}
        order = []
        for c in contacts:
            L = int(c["layer"])
            if L not in layers:
                if order and L < order[-1]:
                    violations.append(_violation("layer", reason="layer_index_decreased", hit=c["i"], layer=L))
                order.append(L)
                layers[L] = []
            layers[L].append(float(c["p"][1]))
        for prev, nxt in zip(order, order[1:]):
            if min(layers[nxt]) >= min(layers[prev]) - 1e-6:
                violations.append(_violation("layer", reason="layer_not_below_previous",
                                             layer=nxt, z=min(layers[nxt]), previous_min=min(layers[prev])))
        if order[-1] > order[0] and float(contacts[-1]["p"][1]) >= z0 - 1e-6:
            violations.append(_violation("layer", reason="no_net_descent"))

    gain = max((e_out - e_in for e_in, e_out in energies), default=0.0)
    summary = dict(
        contacts=len(contacts),
        violations=len(violations),
        max_energy_gain_j_per_kg=float(gain),
        min_proxy_clearance_m=None if min_clearance is np.inf else float(min_clearance),
        min_plate_proxy_clearance_m=None if min_plate is np.inf else float(min_plate),
        max_contact_penetration_m=float(max(0.0, max_penetration)),
        clearance_check="continuous capsule proxy (polynomial critical points + samples)",
        full_triangle_mesh="not run",
        probe_point_keepout_pairs="not run",
        scope=route.get("scope", "excerpt"),
        per_flight_proxy_clearance_m=per_flight_clearance,
    )
    return dict(ok=not violations, violations=violations, summary=summary)


def audit_plan(plan, **kwargs):
    """Audit the descent block stored on a scene-style plan."""
    route = dict(plan["descent"]["route"])
    route["g"] = plan["g"]
    route["marble_radius"] = plan["R"]
    route["hits"] = plan["descent"]["hits"]
    return audit_route(route, **kwargs)
