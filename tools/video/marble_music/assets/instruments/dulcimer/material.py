"""dulcimer materials"""
def shared(C):
    return {'spruce': C.add_wood(C.mat('dc_spruce',(0.75,0.58,0.36),rough=0.45,coat=0.3),(0.68,0.50,0.30),(0.85,0.68,0.45),scale=5.0),
            'walnut': C.add_wood(C.mat('dc_walnut',(0.22,0.11,0.05),rough=0.35,coat=0.6),(0.12,0.05,0.02),(0.32,0.16,0.07),scale=8.0),
            'silver': C.mat('dc_silver',(0.88,0.88,0.9),rough=0.15,metal=1.0), 'gold': C.mat('dc_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0),
            'dark': C.mat('dc_dark',(0.06,0.03,0.02),rough=0.6)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.25,0.12,0.06),rough=0.3,coat=0.7),(0.14,0.06,0.025),(0.36,0.18,0.08),scale=8.0)
