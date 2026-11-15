"""harmonica materials"""
def shared(C):
    return {'comb': C.add_wood(C.mat('hm_comb',(0.6,0.38,0.16),rough=0.4,coat=0.4),(0.5,0.3,0.12),(0.72,0.48,0.22),scale=10.0),
            'dark': C.mat('hm_dark',(0.01,0.01,0.01),rough=0.8), 'tin': C.mat('hm_tin',(0.6,0.03,0.03),rough=0.25,metal=0.4,coat=0.8),
            'velvet': C.mat('hm_velvet',(0.03,0.06,0.3),rough=0.95), 'gold': C.mat('hm_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.88,0.89,0.92),rough=0.08,metal=1.0)
