"""ocarina v4: deeper, more saturated celadon glaze; near-black holes."""
def shared(C):
    return {'dark': C.mat('oc4_dark',(0.003,0.004,0.003),rough=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.04,0.32,0.20),rough=0.35,coat=0.5,coat_rough=0.12)
