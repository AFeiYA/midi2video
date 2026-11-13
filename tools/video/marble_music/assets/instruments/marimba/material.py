"""marimba materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    return {'cord': C.mat('mar_cord',(0.08,0.07,0.06),rough=0.7), 'resonator': C.mat('mar_res',(0.25,0.16,0.08),rough=0.35,metal=1.0),
            'dark': C.mat('mar_dark',(0.02,0.015,0.01),rough=0.8)}
def body(C, name, j, note, variant):
    m = C.mat(name,(0.45,0.16,0.07),rough=0.4,coat=0.3); return C.add_wood(m,(0.30,0.09,0.04),(0.62,0.26,0.11))
