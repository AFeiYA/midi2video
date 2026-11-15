"""english_horn materials"""
def shared(C):
    return {'keys': C.mat('eh_keys',(0.9, 0.9, 0.92),rough=0.12,metal=1.0), 'dark': C.mat('eh_dark',(0.01,0.008,0.006),rough=0.6), 'cork': C.mat('eh_cork',(0.55,0.38,0.22),rough=0.8), 'thread': C.mat('eh_thread',(0.1,0.25,0.75),rough=0.6), 'cane': C.mat('eh_cane',(0.82,0.66,0.35),rough=0.45,coat=0.3)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.1, 0.035, 0.012),rough=0.25,coat=0.8),(0.06, 0.02, 0.007),(0.15, 0.055, 0.02),scale=6.0)
