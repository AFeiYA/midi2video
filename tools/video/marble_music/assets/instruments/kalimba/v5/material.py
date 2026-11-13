"""kalimba materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    m = C.mat('kal_wood',(0.25,0.13,0.06),rough=0.3,coat=0.6)
    return {'steel': C.mat('kal_steel',(0.62,0.64,0.68),rough=0.18,metal=1.0), 'wood': C.add_wood(m,(0.16,0.08,0.03),(0.36,0.20,0.09)),
            'dark': C.mat('kal_dark',(0.01,0.008,0.006),rough=0.9)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.72,0.75,0.80),rough=0.12,metal=1.0)
