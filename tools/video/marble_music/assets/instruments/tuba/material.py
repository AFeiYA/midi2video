"""tuba materials"""
def shared(C):
    return {'trim': C.mat('tu_trim',(0.9, 0.9, 0.92),rough=0.16,metal=1.0), 'dark': C.mat('tu_dark',(0.02,0.015,0.01),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.78, 0.5, 0.16),rough=0.16,metal=1.0)
