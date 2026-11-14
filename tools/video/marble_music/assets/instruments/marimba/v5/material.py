"""marimba v5 materials: deep rosewood bars, dark frame, brass nodes."""
def shared(C):
    return {'cord': C.mat('mar5_cord',(0.6,0.03,0.03),rough=0.7), 'dark': C.mat('mar5_dark',(0.02,0.018,0.015),rough=0.35,coat=0.5),
            'bars': C.add_wood(C.mat('mar5_bars',(0.2,0.05,0.02),rough=0.35,coat=0.5),(0.09,0.02,0.008),(0.30,0.09,0.035)),
            'brass': C.mat('mar5_brass',(0.9,0.65,0.3),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    m = C.mat(name,(0.2,0.05,0.02),rough=0.35,coat=0.5); return C.add_wood(m,(0.10,0.022,0.008),(0.30,0.09,0.035))
