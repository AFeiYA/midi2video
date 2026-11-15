"""celesta materials"""
def shared(C):
    return {'wood': C.add_wood(C.mat('ce_wood',(0.55,0.32,0.12),rough=0.3,coat=0.7),(0.42,0.22,0.08),(0.70,0.45,0.20),scale=7.0),
            'gold': C.mat('ce_gold',(0.95,0.74,0.36),rough=0.18,metal=1.0), 'dark': C.mat('ce_dark',(0.05,0.03,0.02),rough=0.7)}

def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.93,0.89,0.80),rough=0.16,coat=0.7)
