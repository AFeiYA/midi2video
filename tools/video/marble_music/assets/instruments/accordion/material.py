"""accordion materials (pearl = red pearloid celluloid)"""
def shared(C):
    return {'pearl': C.mat('ac_pearl',(0.55,0.02,0.03),rough=0.12,coat=1.0), 'chrome': C.mat('ac_chrome',(0.9,0.9,0.92),rough=0.1,metal=1.0),
            'bel_dark': C.mat('ac_bdark',(0.02,0.02,0.025),rough=0.5), 'bel_white': C.mat('ac_bwhite',(0.85,0.84,0.8),rough=0.5),
            'button': C.mat('ac_button',(0.92,0.9,0.85),rough=0.2,coat=0.6)}

def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.015,0.015,0.017),rough=0.12,coat=1.0)
    return C.mat(name,(0.93,0.89,0.80),rough=0.16,coat=0.7)
