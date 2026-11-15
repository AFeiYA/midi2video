"""rhodes materials"""
def shared(C):
    return {'tolex': C.mat('rh_tolex',(0.02,0.02,0.02),rough=0.85), 'silver': C.mat('rh_silver',(0.8,0.8,0.82),rough=0.3,metal=1.0,aniso=0.6),
            'red': C.mat('rh_red',(0.75,0.08,0.03),rough=0.35,coat=0.5), 'dark': C.mat('rh_dark',(0.01,0.01,0.01),rough=0.6),
            'sparkle': C.mat('rh_sparkle',(0.62,0.62,0.66),rough=0.35,metal=0.25,coat=0.6)}

def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.93,0.89,0.80),rough=0.16,coat=0.7)
