"""sitar materials"""
def shared(C):
    return {'gourd': C.mat('si_gourd',(0.28,0.09,0.02),rough=0.2,coat=1.0), 'ivory': C.mat('si_ivory',(0.9,0.86,0.75),rough=0.3,coat=0.5), 'brass': C.mat('si_brass',(0.92, 0.66, 0.3),rough=0.12,metal=1.0), 'steel': C.mat('si_steel',(0.9, 0.9, 0.9),rough=0.2,metal=1.0)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.06,0.028,0.012),rough=0.3,coat=0.8),(0.035,0.016,0.007),(0.09,0.045,0.02),scale=6.0)
