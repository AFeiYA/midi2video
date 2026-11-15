"""clarinet materials"""
def shared(C):
    return {'keys': C.mat('cl_keys',(0.95, 0.95, 0.97),rough=0.08,metal=1.0), 'dark': C.mat('cl_dark',(0.004,0.004,0.004),rough=0.6), 'pad': C.mat('cl_pad',(0.85,0.75,0.55),rough=0.6), 'mouth': C.mat('cl_mouth',(0.012,0.012,0.014),rough=0.15,coat=1.0), 'reed': C.mat('cl_reed',(0.82,0.66,0.35),rough=0.45)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.022, 0.016, 0.014),rough=0.2,coat=1.0),(0.012, 0.009, 0.008),(0.045, 0.03, 0.025),scale=5.0)
