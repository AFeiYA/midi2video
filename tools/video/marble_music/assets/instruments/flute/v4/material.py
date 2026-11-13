"""flute v4: bright silver tube, gold-plated keys/rings/rod, dark leather pads."""
def shared(C):
    return {'pad': C.mat('fl4_pad',(0.05,0.03,0.02),rough=0.6), 'rod': C.mat('fl4_gold',(0.95,0.68,0.25),rough=0.12,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.92,0.92,0.93),rough=0.1,metal=1.0)
