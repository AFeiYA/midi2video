"""Wall panels for an hscroll scene.

v1 and v2 families sit side by side, x increasing. A descending layer can run
back across the same x, so the old midpoint chain reverses and the planes
overlap. Two coplanar wall panels z-fight; the brick shader then reads as a
black-and-white triangle strip. Overlapping spans become one panel.
"""


def _interval(family):
    a = float(family["x0"])
    b = float(family["x1"])
    return (a, b) if a <= b else (b, a)


def _overlaps(spans):
    order = sorted(spans)
    return any(order[i + 1][0] < order[i][1] - 1e-4 for i in range(len(order) - 1))


def wall_spans(families, x_lo, x_hi):
    """Non-overlapping ``(x0, x1, family)`` panels covering ``[x_lo, x_hi]``.

    ``family`` is None when the layers share x and no divider should be drawn.
    Disjoint left-to-right families keep a panel each, with the boundary at
    the midpoint, matching the original hscroll wall.
    """
    if not families:
        return [(float(x_lo), float(x_hi), None)]
    spans = [_interval(fm) for fm in families]
    chain = [float(x_lo)]
    for q in range(len(families) - 1):
        chain.append((float(families[q]["x1"]) + float(families[q + 1]["x0"])) / 2.0)
    chain.append(float(x_hi))
    reversed_chain = any(chain[q + 1] < chain[q] - 1e-6 for q in range(len(chain) - 1))
    if _overlaps(spans) or reversed_chain:
        return [(float(x_lo), float(x_hi), None)]
    panels = []
    for q, fm in enumerate(families):
        a, b = chain[q], chain[q + 1]
        if b < a:
            a, b = b, a
        if b - a < 1e-4:
            continue
        panels.append((a, b, fm))
    return panels or [(float(x_lo), float(x_hi), None)]
