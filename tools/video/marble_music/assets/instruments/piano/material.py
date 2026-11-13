"""piano materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    return {'rail': C.mat('pno_rail',(0.02,0.02,0.022),rough=0.25,coat=0.8), 'felt': C.mat('pno_felt',(0.45,0.03,0.05),rough=0.95)}
def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.92,0.88,0.78),rough=0.18,coat=0.6)
