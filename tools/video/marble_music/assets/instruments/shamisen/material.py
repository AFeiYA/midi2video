"""shamisen materials"""
def shared(C):
    return {'neck': C.add_wood(C.mat('sh_neck',(0.08,0.015,0.01),rough=0.25,coat=0.9),(0.05,0.008,0.005),(0.12,0.03,0.015),scale=6.0), 'frame': C.add_wood(C.mat('sh_frame',(0.09, 0.03, 0.012),rough=0.3,coat=0.7),(0.06, 0.02, 0.008),(0.13, 0.05, 0.02),scale=6.0), 'skin': C.mat('sh_skin',(0.93,0.91,0.86),rough=0.6), 'ivory': C.mat('sh_ivory',(0.92,0.88,0.78),rough=0.25,coat=0.6), 'silk': C.mat('sh_silk',(0.95,0.9,0.7),rough=0.5), 'red': C.mat('sh_red',(0.6,0.02,0.03),rough=0.7), 'patch': C.mat('sh_patch',(0.75,0.68,0.55),rough=0.6), 'gold': C.mat('sh_gold',(1.0, 0.75, 0.35),rough=0.12,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.012,0.01,0.01),rough=0.12,coat=1.0)
