"""pizzicato materials: body = front violin (golden), v2/v3 = the two behind"""
def shared(C):
    return {'gut': C.mat('pz_gut',(0.7,0.58,0.38),rough=0.4), 'ebony': C.mat('pz_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5),
            'v2': C.add_wood(C.mat('pz_v2',(0.55,0.22,0.06),rough=0.25,coat=0.8),(0.42,0.15,0.04),(0.68,0.3,0.1),scale=6.0),
            'v3': C.add_wood(C.mat('pz_v3',(0.32,0.09,0.03),rough=0.25,coat=0.8),(0.22,0.06,0.02),(0.42,0.13,0.05),scale=6.0),
            'dark': C.mat('pz_dark',(0.02,0.01,0.005),rough=0.7)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.75,0.45,0.12),rough=0.25,coat=0.8),(0.62,0.34,0.08),(0.88,0.58,0.2),scale=6.0)
