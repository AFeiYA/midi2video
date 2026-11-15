"""pan_flute materials"""
def shared(C):
    return {'cord': C.mat('pf_cord',(0.75,0.06,0.04),rough=0.7), 'pipe': C.add_wood(C.mat('pf_pipe',(0.72,0.55,0.26),rough=0.35,coat=0.5),(0.6,0.42,0.17),(0.82,0.66,0.34),scale=2.0), 'dark': C.mat('pf_dark',(0.02,0.012,0.005),rough=0.7), 'node': C.mat('pf_node',(0.45,0.3,0.12),rough=0.4,coat=0.4)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.62, 0.45, 0.2),rough=0.35,coat=0.5),(0.5, 0.34, 0.13),(0.75, 0.58, 0.3),scale=2.0)
