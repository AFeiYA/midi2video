"""castanets materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    return {'dark': C.mat('cast_dark',(0.03,0.012,0.006),rough=0.6), 'cord': C.mat('cast_cord',(0.55,0.05,0.04),rough=0.8)}
def body(C, name, j, note, variant):
    m = C.mat(name,(0.25,0.08,0.04),rough=0.35,coat=0.5); return C.add_wood(m,(0.16,0.05,0.02),(0.42,0.16,0.07))
