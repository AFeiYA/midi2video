"""nylon_guitar materials"""
def shared(C):
    return {'nylon': C.mat('ng_nylon',(0.92,0.9,0.84),rough=0.25,coat=0.6), 'wound': C.mat('ng_wound',(0.75,0.72,0.66),rough=0.3,metal=1.0),
            'rosewood': C.add_wood(C.mat('ng_rose',(0.08,0.03,0.015),rough=0.35,coat=0.5),(0.04,0.015,0.008),(0.14,0.06,0.025),scale=9.0),
            'dark': C.mat('ng_dark',(0.006,0.004,0.003),rough=0.9), 'mosaic': C.mat('ng_mosaic',(0.06,0.25,0.12),rough=0.4,coat=0.5)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.72,0.5,0.24),rough=0.35,coat=0.6),(0.62,0.4,0.17),(0.84,0.62,0.32),scale=6.0)
