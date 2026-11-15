"""cello materials (bow: stick / hair / frog = ebony / tip = pearl)"""
def shared(C):
    return {
    'ebony': C.mat('cel_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5), 'dark': C.mat('cel_dark',(0.03,0.012,0.005),rough=0.6),
    'steel': C.mat('cel_steel',(0.8,0.8,0.78),rough=0.25,metal=1.0), 'pale': C.mat('cel_pale',(0.85,0.74,0.55),rough=0.4),
    'stick': C.add_wood(C.mat('cel_stick',(0.2,0.07,0.02),rough=0.3,coat=0.6),(0.12,0.04,0.01),(0.3,0.11,0.03),scale=12.0),
    'hair': C.mat('cel_hair',(0.92,0.9,0.84),rough=0.6), 'pearl': C.mat('cel_pearl',(0.85,0.88,0.9),rough=0.1,coat=1.0)}

def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.28, 0.05, 0.015),rough=0.25,coat=0.85),(0.18, 0.03, 0.01),(0.36, 0.07, 0.02),scale=6.0)
