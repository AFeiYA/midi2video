"""bassoon materials"""
def shared(C):
    return {'keys': C.mat('bn_keys',(0.9, 0.9, 0.92),rough=0.12,metal=1.0), 'dark': C.mat('bn_dark',(0.012,0.01,0.01),rough=0.4,coat=0.5), 'ivory': C.mat('bn_ivory',(0.92,0.88,0.78),rough=0.25,coat=0.6), 'cork': C.mat('bn_cork',(0.55,0.38,0.22),rough=0.8), 'thread': C.mat('bn_thread',(0.75,0.08,0.06),rough=0.6), 'cane': C.mat('bn_cane',(0.82,0.66,0.35),rough=0.45,coat=0.3)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.17, 0.045, 0.012),rough=0.25,coat=0.8),(0.11, 0.028, 0.007),(0.26, 0.075, 0.02),scale=4.0)
