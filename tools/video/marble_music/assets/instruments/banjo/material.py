"""banjo materials"""
def shared(C):
    return {'maple': C.add_wood(C.mat('bj_maple',(0.5, 0.3, 0.12),rough=0.3,coat=0.7),(0.38, 0.21, 0.08),(0.62, 0.4, 0.18),scale=8.0), 'board': C.mat('bj_board',(0.015,0.01,0.008),rough=0.35,coat=0.5), 'head': C.mat('bj_head',(0.92,0.9,0.85),rough=0.65), 'chrome': C.mat('bj_chrome',(0.92, 0.92, 0.94),rough=0.08,metal=1.0), 'rim': C.add_wood(C.mat('bj_rim',(0.14, 0.05, 0.015),rough=0.3,coat=0.7),(0.09, 0.03, 0.01),(0.2, 0.08, 0.03),scale=6.0), 'pearl': C.mat('bj_pearl',(0.9,0.9,0.86),rough=0.1,coat=1.0), 'steel': C.mat('bj_steel',(0.9, 0.9, 0.9),rough=0.2,metal=1.0), 'bridge': C.mat('bj_bridge',(0.55,0.36,0.17),rough=0.4), 'brass': C.mat('bj_brass',(0.92, 0.66, 0.3),rough=0.12,metal=1.0)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.07,0.035,0.015),rough=0.3,coat=0.8),(0.04,0.02,0.008),(0.11,0.055,0.025),scale=5.0)
