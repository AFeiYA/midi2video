"""xylophone v7: bars still coloured by pitch class (same palette as v5)."""
def shared(C):
    return {}
def body(C, name, j, note, variant):
    return C.mat(name, C.pitch_rgb(note), rough=0.38, coat=0.2, coat_rough=0.15)
