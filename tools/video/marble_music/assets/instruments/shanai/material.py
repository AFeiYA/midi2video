"""shanai materials"""
def shared(C):
    return {'brass': C.mat('sn_brass',(0.92, 0.66, 0.3),rough=0.12,metal=1.0), 'dark': C.mat('sn_dark',(0.01,0.006,0.003),rough=0.7), 'reed': C.mat('sn_reed',(0.8,0.65,0.35),rough=0.5), 'thread': C.mat('sn_thread',(0.7,0.04,0.04),rough=0.6), 'ivory': C.mat('sn_ivory',(0.92,0.88,0.78),rough=0.3)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.07,0.03,0.012),rough=0.25,coat=0.9),(0.04,0.017,0.007),(0.11,0.05,0.02),scale=6.0)
