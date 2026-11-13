"""ocarina materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    return {'dark': C.mat('oc_dark',(0.02,0.025,0.02),rough=0.9)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.26,0.47,0.36),rough=0.4,coat=1.0,coat_rough=0.03)
