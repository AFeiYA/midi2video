"""Labeled trajectory figures. SVG only, so the artifacts stay text.

The descent figure is the free-flight excerpt. The rail figure is the separate
guide transition. Neither figure is a render, and the rail is not in the
scene builder.
"""

import json


def _bounds(points, pad=0.4):
    xs = [p[0] for p in points]
    zs = [p[1] for p in points]
    return min(xs) - pad, max(xs) + pad, min(zs) - pad, max(zs) + pad


def _svg_header(x0, x1, z0, z1, title):
    width, height = 1100, 760
    span_x = max(x1 - x0, 0.1)
    span_z = max(z1 - z0, 0.1)
    scale = min((width - 280) / span_x, (height - 80) / span_z)
    def X(x):
        return 50 + (x - x0) * scale
    def Y(z):
        return 30 + (z1 - z) * scale
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<rect width="100%" height="100%" fill="#14141c"/>',
        f'<text x="50" y="22" fill="#f4f1ea" font-family="ui-sans-serif,sans-serif" font-size="16">{title}</text>',
    ]
    return parts, X, Y, scale


def write_descent_svg(plan, path):
    route = plan["descent"]["route"]
    g = plan["g"]
    frames = plan["marble"]
    contacts = route["contacts"]
    flights = route["flights"]
    clearances = plan["descent"]["per_flight_proxy_clearance_m"]
    points = [tuple(p) for p in frames]
    for contact in contacts:
        points.append(tuple(contact["p"]))
    x0, x1, z0, z1 = _bounds(points, 0.8)
    parts, X, Y, _scale = _svg_header(x0, x1, z0, z1, "Descending-layer hscroll excerpt (proxy, not a render)")
    colors = ["#8fd3ff", "#f2c14e", "#7dce82", "#e07a8d", "#c9b6ff", "#f0a06a"]
    # Path, colored by the layer of the next contact.
    layer_at = []
    for frame_i, (x, z) in enumerate(frames):
        t = frame_i / plan["fps"]
        layer = contacts[0]["layer"]
        for contact in contacts:
            if contact["time"] <= t + 1e-9:
                layer = contact["layer"]
        layer_at.append(layer)
    start = 0
    for i in range(1, len(frames) + 1):
        if i == len(frames) or layer_at[i] != layer_at[start]:
            color = colors[layer_at[start] % len(colors)]
            pts = " ".join(f"{X(frames[k][0]):.1f},{Y(frames[k][1]):.1f}" for k in range(start, i))
            parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="2.2" points="{pts}"/>')
            start = i
    for contact in contacts:
        color = colors[contact["layer"] % len(colors)]
        normal = contact["normal"]
        tangent = (-normal[1], normal[0])
        half = contact["half_length"]
        cx, cz = contact["plate_center"]
        x_a, z_a = cx - tangent[0] * half, cz - tangent[1] * half
        x_b, z_b = cx + tangent[0] * half, cz + tangent[1] * half
        parts.append(
            f'<line x1="{X(x_a):.1f}" y1="{Y(z_a):.1f}" x2="{X(x_b):.1f}" y2="{Y(z_b):.1f}" '
            f'stroke="{color}" stroke-width="4" stroke-linecap="round"/>'
        )
        px, pz = contact["p"]
        parts.append(f'<circle cx="{X(px):.1f}" cy="{Y(pz):.1f}" r="3.2" fill="#fff"/>')
        energy = 0.5 * (contact["vin"][0] ** 2 + contact["vin"][1] ** 2) + g * contact["p"][1]
        # Outgoing flight sits one slot after the lead-in.
        gap = clearances[contact["i"] + 1] if contact["i"] + 1 < len(clearances) else None
        gap_txt = "n/a" if gap is None else f"{gap * 1000:.0f} mm"
        label = f"t={contact['time']:.2f}s L{contact['layer']} {contact['mount']} E={energy:.1f} clr {gap_txt}"
        anchor_x = X(px) + 8
        anchor_y = Y(pz) - 8 - (contact["i"] % 3) * 11
        parts.append(
            f'<text x="{anchor_x:.1f}" y="{anchor_y:.1f}" fill="#d9d4c8" '
            f'font-family="ui-sans-serif,sans-serif" font-size="10">{label}</text>'
        )
    summary = plan["validation"]
    notes = [
        f"scope: {summary['scope']}",
        "check: continuous capsule proxy. Full triangle mesh: not run. Probe keep-out/pairs: not run.",
        f"min proxy gap {summary['min_proxy_clearance_m']:.3f} m; max energy gain {summary['max_energy_gain_j_per_kg']:.2e} J/kg",
        "Whole song: not validated. Camera may follow down; world height is not held in a band.",
        "Local ballistic lobs are allowed. A new layer still opens below the previous one.",
        f"flights {len(flights)}; g={g} m/s^2; passive frictionless strikes, restitution <= 1",
    ]
    y = 48
    for line in notes:
        parts.append(f'<text x="50" y="{y}" fill="#b7b1a6" font-family="ui-sans-serif,sans-serif" font-size="12">{line}</text>')
        y += 16
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(parts) + "\n")


def write_rail_svg(result, path):
    phases = result["phases"]
    points = []
    for phase in phases:
        for sample in phase["samples"]:
            points.append(sample["p"])
    x0, x1, z0, z1 = _bounds(points, 0.35)
    parts, X, Y, _scale = _svg_header(
        x0, x1, z0, z1,
        "Passive guide: fall, slip capture, rolling U-turn, tangent exit (not rendered)",
    )
    style = {
        "fall": "#8fd3ff",
        "capture": "#f2c14e",
        "rail": "#e07a8d",
        "exit_flight": "#7dce82",
    }
    for phase in phases:
        color = style.get(phase["name"], "#fff")
        pts = " ".join(f"{X(s['p'][0]):.1f},{Y(s['p'][1]):.1f}" for s in phase["samples"])
        parts.append(f'<polyline fill="none" stroke="{color}" stroke-width="3" points="{pts}"/>')
    rail = next(phase for phase in phases if phase["name"] == "rail")
    valley = min(rail["samples"], key=lambda row: row["z"])
    lip = rail["samples"][-1]
    for sample, name in ((rail["samples"][0], "capture"), (valley, "valley"), (lip, "lip / tangent exit")):
        parts.append(f'<circle cx="{X(sample["p"][0]):.1f}" cy="{Y(sample["p"][1]):.1f}" r="4" fill="#fff"/>')
        parts.append(
            f'<text x="{X(sample["p"][0]) + 8:.1f}" y="{Y(sample["p"][1]) - 8:.1f}" fill="#f4f1ea" '
            f'font-family="ui-sans-serif,sans-serif" font-size="12">{name} z={sample["z"]:.2f}m '
            f'v={sample["speed"]:.2f}</text>'
        )
    fall = phases[0]
    parts.append(
        f'<text x="{X(fall["samples"][0]["p"][0]):.1f}" y="{Y(fall["samples"][0]["p"][1]) - 14:.1f}" '
        f'fill="#8fd3ff" font-family="ui-sans-serif,sans-serif" font-size="12">'
        f'incoming v={result["speed_at_launch"]:.2f} -> capture v={result["speed_at_capture"]:.2f} (fall sped up)</text>'
    )
    land = result["landing"]["p"]
    parts.append(f'<circle cx="{X(land[0]):.1f}" cy="{Y(land[1]):.1f}" r="5" fill="#7dce82"/>')
    parts.append(
        f'<text x="{X(land[0]) + 8:.1f}" y="{Y(land[1]) + 16:.1f}" fill="#7dce82" '
        f'font-family="ui-sans-serif,sans-serif" font-size="12">next strike t={result["dt_s"]:.3f}s '
        f'z={land[1]:.2f}</text>'
    )
    notes = [
        "Not renderer-supported. No spring kicker. Constraint force on the rail does no work.",
        f"Slip capture removes {phases[1]['energy_loss_j_per_kg']:.2f} J/kg by kinetic friction. Velocity stays continuous.",
        f"Valley z={rail['z_valley']:.2f} then lip z={rail['z_exit']:.2f}: a local rise paid by the drop and incoming speed.",
        "Rolling model: solid sphere, no slip, spin energy included. Overall landing is below the start.",
    ]
    y = 48
    for line in notes:
        parts.append(f'<text x="40" y="{y}" fill="#b7b1a6" font-family="ui-sans-serif,sans-serif" font-size="12">{line}</text>')
        y += 16
    parts.append("</svg>")
    with open(path, "w", encoding="utf-8") as handle:
        handle.write("\n".join(parts) + "\n")


def main():
    import argparse
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("plan")
    ap.add_argument("svg")
    ap.add_argument("--rail", action="store_true")
    args = ap.parse_args()
    payload = json.load(open(args.plan))
    if args.rail:
        write_rail_svg(payload, args.svg)
    else:
        write_descent_svg(payload, args.svg)
    print("wrote", args.svg)


if __name__ == "__main__":
    main()
