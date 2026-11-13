"""glockenspiel materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    m = C.mat('gl_wood',(0.15,0.08,0.04),rough=0.35,coat=0.5)
    return {'wood': C.add_wood(m,(0.09,0.05,0.025),(0.24,0.13,0.06)), 'screw': C.mat('gl_screw',(0.45,0.45,0.47),rough=0.2,metal=1.0),
            'felt': C.mat('gl_felt',(0.55,0.04,0.05),rough=0.95)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.82,0.84,0.87),rough=0.05,metal=1.0)
