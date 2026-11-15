"""harp materials"""
def shared(C):
    return {'gold': C.mat('hp_gold',(0.95,0.72,0.35),rough=0.22,metal=1.0),
            'maple': C.add_wood(C.mat('hp_maple',(0.72,0.5,0.26),rough=0.35,coat=0.6),(0.64,0.42,0.2),(0.85,0.64,0.36),scale=6.0),
            's_cream': C.mat('hp_scream',(0.88,0.84,0.72),rough=0.35), 's_red': C.mat('hp_sred',(0.7,0.03,0.03),rough=0.35),
            's_blue': C.mat('hp_sblue',(0.04,0.08,0.45),rough=0.35)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.95,0.74,0.36),rough=0.2,metal=1.0)
