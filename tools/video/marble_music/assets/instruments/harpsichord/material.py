"""harpsichord materials: reversed keys (natural shape = ebony, sharp shape = bone)"""
def shared(C):
    return {'lacquer': C.mat('hc_lacquer',(0.42,0.025,0.02),rough=0.18,coat=1.0), 'gold': C.mat('hc_gold',(0.95,0.72,0.35),rough=0.22,metal=1.0),
            'bone': C.mat('hc_bone',(0.9,0.86,0.76),rough=0.25,coat=0.4), 'ebony': C.mat('hc_ebony',(0.015,0.012,0.012),rough=0.2,coat=0.8),
            'paint': C.mat('hc_paint',(0.32,0.55,0.62),rough=0.6)}
def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.9,0.86,0.76),rough=0.22,coat=0.5)
    return C.mat(name,(0.015,0.012,0.012),rough=0.14,coat=1.0)
