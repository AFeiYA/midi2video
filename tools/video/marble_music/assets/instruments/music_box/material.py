"""music_box materials"""
def shared(C):
    return {'wood': C.add_wood(C.mat('mb_wood',(0.25,0.12,0.06),rough=0.3,coat=0.8),(0.12,0.05,0.02),(0.38,0.19,0.08),scale=8.0),
            'velvet': C.mat('mb_velvet',(0.45,0.02,0.04),rough=0.95), 'brass': C.mat('mb_brass',(0.9,0.66,0.3),rough=0.18,metal=1.0),
            'dark': C.mat('mb_dark',(0.03,0.02,0.015),rough=0.4,metal=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.95,0.75,0.38),rough=0.1,metal=1.0)
