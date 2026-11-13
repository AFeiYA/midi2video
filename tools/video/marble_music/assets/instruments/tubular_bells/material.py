"""tubular_bells materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    return {'cap': C.mat('tb_cap',(0.80,0.50,0.16),rough=0.12,metal=1.0), 'dark': C.mat('tb_dark',(0.05,0.03,0.01),rough=0.6,metal=0.5),
            'cord': C.mat('tb_cord',(0.15,0.12,0.1),rough=0.8)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.88,0.58,0.18),rough=0.16,metal=1.0)
