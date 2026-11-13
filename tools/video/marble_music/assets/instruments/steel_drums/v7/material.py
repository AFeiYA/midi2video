"""steel drums v7: slightly rougher chrome than v5 so bloom does not blow the pan out."""
def shared(C):
    return {'pan': C.mat('sd7_pan', (0.86, 0.87, 0.90), rough=0.12, metal=1.0),
            'dark': C.mat('sd7_dark', (0.15, 0.15, 0.16), rough=0.45, metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name, (0.94, 0.94, 0.95), rough=0.10, metal=1.0)
