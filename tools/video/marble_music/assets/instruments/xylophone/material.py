"""xylophone materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
import colorsys
def shared(C):
    m = C.mat('xy_frame',(0.8,0.68,0.5),rough=0.45,coat=0.3)
    return {'felt': C.mat('xy_felt',(0.6,0.05,0.06),rough=0.95), 'frame': C.add_wood(m,(0.70,0.58,0.40),(0.88,0.78,0.60))}
def body(C, name, j, note, variant):
    return C.mat(name, colorsys.hsv_to_rgb((j%7)/7.0,0.72,0.85), rough=0.3, coat=0.7)
