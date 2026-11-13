"""xylophone v5 materials (bars coloured by pitch class with the shared palette, matching piano v5): shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
import colorsys
def shared(C):
    m = C.mat('xy_frame',(0.8,0.68,0.5),rough=0.45,coat=0.3)
    return {'felt': C.mat('xy_felt',(0.6,0.05,0.06),rough=0.95), 'frame': C.add_wood(m,(0.70,0.58,0.40),(0.88,0.78,0.60))}
def body(C, name, j, note, variant):
    return C.mat(name, C.pitch_rgb(note), rough=0.3, coat=0.7)
