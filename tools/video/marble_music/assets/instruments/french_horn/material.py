"""french_horn materials"""
def shared(C):
    return {'trim': C.mat('fh_trim',(0.9, 0.9, 0.92),rough=0.16,metal=1.0), 'dark': C.mat('fh_dark',(0.02,0.015,0.01),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.9, 0.52, 0.33),rough=0.16,metal=1.0)
