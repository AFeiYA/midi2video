"""shakuhachi materials"""
def shared(C):
    return {'node': C.mat('sk_node',(0.08,0.055,0.015),rough=0.35,coat=0.6), 'dark': C.mat('sk_dark',(0.015,0.01,0.004),rough=0.7), 'inlay': C.mat('sk_inlay',(0.93,0.9,0.82),rough=0.2,coat=0.8), 'cord': C.mat('sk_cord',(0.35,0.06,0.45),rough=0.6)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.17, 0.15, 0.035),rough=0.3,coat=0.7),(0.12, 0.1, 0.02),(0.24, 0.21, 0.06),scale=1.5)
