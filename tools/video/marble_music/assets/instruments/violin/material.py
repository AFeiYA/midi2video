"""violin materials"""
def shared(C):
    return {
    'ebony': C.mat('vio_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5), 'dark': C.mat('vio_dark',(0.03,0.012,0.005),rough=0.6),
    'steel': C.mat('vio_steel',(0.8,0.8,0.78),rough=0.25,metal=1.0), 'pale': C.mat('vio_pale',(0.85,0.74,0.55),rough=0.4),
    'stick': C.add_wood(C.mat('vio_stick',(0.2,0.07,0.02),rough=0.3,coat=0.6),(0.12,0.04,0.01),(0.3,0.11,0.03),scale=12.0),
    'hair': C.mat('vio_hair',(0.92,0.9,0.84),rough=0.6), 'pearl': C.mat('vio_pearl',(0.85,0.88,0.9),rough=0.1,coat=1.0)}

def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.62, 0.15, 0.02),rough=0.25,coat=0.85),(0.45, 0.08, 0.01),(0.75, 0.2, 0.03),scale=6.0)
