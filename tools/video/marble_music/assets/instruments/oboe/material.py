"""oboe materials"""
def shared(C):
    return {'keys': C.mat('ob_keys',(0.9, 0.9, 0.92),rough=0.12,metal=1.0), 'dark': C.mat('ob_dark',(0.01,0.008,0.006),rough=0.6), 'cork': C.mat('ob_cork',(0.55,0.38,0.22),rough=0.8), 'thread': C.mat('ob_thread',(0.95,0.35,0.05),rough=0.6), 'cane': C.mat('ob_cane',(0.82,0.66,0.35),rough=0.45,coat=0.3)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.03, 0.009, 0.005),rough=0.25,coat=0.8),(0.018, 0.005, 0.003),(0.05, 0.016, 0.008),scale=6.0)
