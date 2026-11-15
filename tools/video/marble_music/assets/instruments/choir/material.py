"""choir materials"""
def shared(C):
    return {'robe': C.mat('ch_robe',(0.32,0.02,0.05),rough=0.7,coat=0.1), 'stole': C.mat('ch_stole',(0.92,0.9,0.84),rough=0.5),
            'skin': C.mat('ch_skin',(0.8,0.55,0.4),rough=0.5), 'hair': C.mat('ch_hair',(0.05,0.03,0.02),rough=0.6),
            'folder': C.mat('ch_folder',(0.02,0.02,0.025),rough=0.4), 'gold': C.mat('ch_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.36,0.2,0.09),rough=0.35,coat=0.6),(0.24,0.12,0.05),(0.5,0.3,0.14),scale=6.0)
