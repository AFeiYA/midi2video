"""distortion_guitar materials"""
def shared(C):
    return {'chrome': C.mat('dg_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0), 'black': C.mat('dg_black',(0.012,0.012,0.012),rough=0.3,coat=0.6),
            'white': C.mat('dg_white',(0.9,0.88,0.84),rough=0.3,coat=0.5),
            'rosewood': C.add_wood(C.mat('dg_rose',(0.08,0.03,0.015),rough=0.35,coat=0.5),(0.04,0.015,0.008),(0.14,0.06,0.025),scale=9.0),
            'gold': C.mat('dg_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0), 'grille': C.mat('dg_grille',(0.05,0.045,0.04),rough=0.9)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.6,0.01,0.015),rough=0.1,coat=1.0)
