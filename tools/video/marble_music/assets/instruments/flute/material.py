"""flute materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    return {'pad': C.mat('fl_pad',(0.85,0.75,0.55),rough=0.6), 'rod': C.mat('fl_rod',(0.95,0.94,0.92),rough=0.1,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.97,0.96,0.94),rough=0.07,metal=1.0)
