"""vibraphone materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    return {'cord': C.mat('vib_cord',(0.35,0.04,0.05),rough=0.7), 'resonator': C.mat('vib_res',(0.85,0.62,0.22),rough=0.25,metal=1.0),
            'dark': C.mat('vib_dark',(0.02,0.02,0.02),rough=0.8)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.88,0.89,0.91),rough=0.32,metal=1.0,aniso=0.7)
