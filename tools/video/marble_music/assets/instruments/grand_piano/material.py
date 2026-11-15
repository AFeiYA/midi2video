"""grand_piano materials: ivory/ebony key by pitch class, black lacquer case, gold trim"""
def shared(C):
    return {'lacquer': C.mat('gp_lacquer',(0.012,0.012,0.014),rough=0.12,coat=1.0), 'gold': C.mat('gp_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0),
            'felt': C.mat('gp_felt',(0.45,0.03,0.05),rough=0.95), 'dark': C.mat('gp_dark',(0.03,0.03,0.03),rough=0.5)}

def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.93,0.89,0.80),rough=0.16,coat=0.7)
