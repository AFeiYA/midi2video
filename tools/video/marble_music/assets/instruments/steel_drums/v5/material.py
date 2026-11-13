"""steel_drums materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    return {'pan': C.mat('sd5_pan',(0.86,0.87,0.9),rough=0.14,metal=1.0), 'dark': C.mat('sd_dark',(0.15,0.15,0.16),rough=0.4,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.96,0.96,0.97),rough=0.02,metal=1.0)
