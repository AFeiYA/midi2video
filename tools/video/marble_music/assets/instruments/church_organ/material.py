"""church_organ materials"""
def shared(C):
    return {'oak': C.add_wood(C.mat('co_oak',(0.22,0.12,0.06),rough=0.4,coat=0.4),(0.12,0.06,0.03),(0.30,0.17,0.08),scale=6.0),
            'tin': C.mat('co_tin',(0.82,0.83,0.86),rough=0.18,metal=1.0), 'gold': C.mat('co_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0),
            'ivory': C.mat('co_ivory',(0.9,0.86,0.76),rough=0.25,coat=0.5), 'dark': C.mat('co_dark',(0.015,0.012,0.01),rough=0.4,coat=0.5)}

def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.93,0.89,0.80),rough=0.16,coat=0.7)
