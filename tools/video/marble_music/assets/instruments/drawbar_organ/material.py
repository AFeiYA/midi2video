"""drawbar_organ materials"""
def shared(C):
    return {'walnut': C.add_wood(C.mat('do_walnut',(0.2,0.09,0.04),rough=0.3,coat=0.7),(0.10,0.04,0.015),(0.30,0.14,0.06),scale=8.0),
            'chrome': C.mat('do_chrome',(0.9,0.9,0.92),rough=0.1,metal=1.0), 'tab_brown': C.mat('do_tbrown',(0.28,0.10,0.04),rough=0.3,coat=0.6),
            'tab_white': C.mat('do_twhite',(0.9,0.88,0.82),rough=0.3,coat=0.5), 'tab_black': C.mat('do_tblack',(0.015,0.015,0.015),rough=0.3,coat=0.6),
            'pale': C.add_wood(C.mat('do_pale',(0.7,0.5,0.28),rough=0.4),(0.62,0.42,0.22),(0.82,0.62,0.38),scale=7.0)}

def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.93,0.89,0.80),rough=0.16,coat=0.7)
