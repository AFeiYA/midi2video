"""tin_whistle materials"""
def shared(C):
    return {'head': C.mat('tw_head',(0.0,0.35,0.1),rough=0.25,coat=0.8), 'dark': C.mat('tw_dark',(0.01,0.01,0.01),rough=0.7), 'edge': C.mat('tw_edge',(0.92,0.92,0.9),rough=0.3), 'leaf': C.mat('tw_leaf',(0.03,0.42,0.08),rough=0.45,coat=0.3)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.88,0.88,0.86),rough=0.1,metal=1.0)
