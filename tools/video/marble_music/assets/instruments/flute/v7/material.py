"""flute v7: maple striker board (slot body, flashes on hit); silver post; gold keys; dark pads."""
def shared(C):
    tube = C.mat('fl7_tube', (0.90, 0.90, 0.92), rough=0.14, metal=1.0)
    return {
        'tube': tube,
        'pad': C.mat('fl7_pad', (0.05, 0.03, 0.02), rough=0.6),
        'rod': C.mat('fl7_gold', (0.95, 0.68, 0.25), rough=0.14, metal=1.0),
    }

def body(C, name, j, note, variant):
    # Light maple board, distinct from the silver post and the grey wall.
    m = C.mat(name, (0.62, 0.42, 0.22), rough=0.35, coat=0.35)
    C.add_wood(m, (0.48, 0.30, 0.14), (0.78, 0.58, 0.32), scale=7.0)
    return m
