"""flute v7: silver tube (slightly rougher than v5 to tame chrome bloom), gold keys, dark pads."""
def shared(C):
    return {'pad': C.mat('fl7_pad', (0.05, 0.03, 0.02), rough=0.6),
            'rod': C.mat('fl7_gold', (0.95, 0.68, 0.25), rough=0.14, metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name, (0.92, 0.92, 0.93), rough=0.16, metal=1.0)
