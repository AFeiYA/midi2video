"""upright_bass materials"""
def shared(C):
    return {'gut': C.mat('ub_gut',(0.55,0.42,0.25),rough=0.45), 'ebony': C.mat('ub_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5),
            'maple': C.mat('ub_maple',(0.82,0.7,0.5),rough=0.4), 'dark': C.mat('ub_dark',(0.05,0.02,0.008),rough=0.6),
            'brass': C.mat('ub_brass',(0.9,0.68,0.3),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.36,0.13,0.03),rough=0.25,coat=0.8),(0.26,0.08,0.02),(0.5,0.2,0.05),scale=6.0)
