"""orchestra_hit materials"""
def shared(C):
    return {'chrome': C.mat('oh_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0), 'copper': C.mat('oh_copper',(0.85,0.42,0.22),rough=0.18,metal=1.0),
            'gold': C.mat('oh_gold',(0.95,0.72,0.3),rough=0.18,metal=1.0), 'black': C.mat('oh_black',(0.02,0.02,0.02),rough=0.4),
            'felt': C.mat('oh_felt',(0.88,0.84,0.76),rough=0.95)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.9,0.85,0.72),rough=0.55)
