"""steel drums v7: the pan itself is the tilted hit surface (playing face toward +Z).
Centre note dome flush with the contact face at z=+0.045; surrounding dimples slightly lower.
No separate rim-bar striker, no face-on backdrop pan."""
import math
def build(C, variant=None):
    # bowl along +Z; rim stays below the contact plane so the marble hits the raised centre note
    pan = C.prim('cyl', 1, loc=(0, 0, -0.05), scale=(0.27, 0.27, 0.16), bevel=0.012, verts=72)
    C.cut(pan, C.prim('cyl', 1, loc=(0, 0, 0.04), scale=(0.245, 0.245, 0.10), verts=72))
    note = C.prim('sphere', 0, loc=(0, 0, 0.005), scale=(0.12, 0.12, 0.04), verts=48)  # top = 0.045
    ring = C.prim('torus', 2, loc=(0, 0, 0.018), scale=(0.122, 0.005), verts=48)
    dimples = []
    for k in range(6):
        t = k * math.pi / 3 + 0.3
        x, y = 0.175 * math.cos(t), 0.175 * math.sin(t)
        dimples.append(C.prim('sphere', 1, loc=(x, y, -0.005), scale=(0.055, 0.055, 0.028), verts=32))
        dimples.append(C.prim('torus', 2, loc=(x, y, 0.008), scale=(0.052, 0.004), verts=32))
    return [pan, note, ring] + dimples
