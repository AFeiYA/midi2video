"""piccolo materials"""
def shared(C):
    return {'pad': C.mat('pc_pad',(0.85,0.75,0.55),rough=0.6), 'rod': C.mat('pc_rod',(0.95, 0.94, 0.92),rough=0.08,metal=1.0), 'dark': C.mat('pc_dark',(0.01,0.01,0.02),rough=0.6), 'case': C.mat('pc_case',(0.02,0.02,0.022),rough=0.35,coat=0.6), 'velvet': C.mat('pc_velvet',(0.015,0.03,0.2),rough=0.95)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.97,0.96,0.94),rough=0.07,metal=1.0)
