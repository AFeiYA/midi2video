"""trombone materials"""
def shared(C):
    return {'trim': C.mat('tb_trim',(0.9, 0.9, 0.92),rough=0.16,metal=1.0), 'dark': C.mat('tb_dark',(0.02,0.015,0.01),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.92, 0.64, 0.24),rough=0.14,metal=1.0)
