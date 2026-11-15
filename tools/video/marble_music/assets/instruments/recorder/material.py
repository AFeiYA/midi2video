"""recorder materials"""
def shared(C):
    return {'ring': C.mat('rc_ring',(0.025,0.011,0.005),rough=0.25,coat=0.8), 'dark': C.mat('rc_dark',(0.01,0.006,0.003),rough=0.7), 'edge': C.mat('rc_edge',(0.9,0.85,0.7),rough=0.3)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.3, 0.15, 0.045),rough=0.3,coat=0.6),(0.22, 0.1, 0.028),(0.4, 0.21, 0.07),scale=7.0)
