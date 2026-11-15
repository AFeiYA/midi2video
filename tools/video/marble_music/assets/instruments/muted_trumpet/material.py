"""muted_trumpet materials"""
def shared(C):
    return {'pearl': C.mat('muted_trumpet_pearl',(0.9,0.9,0.86),rough=0.1,coat=1.0), 'trim': C.mat('muted_trumpet_trim',(0.92, 0.64, 0.24),rough=0.16,metal=1.0),
            'dark': C.mat('muted_trumpet_dark',(0.02,0.015,0.01),rough=0.6), 'mute': C.mat('muted_trumpet_mute',(0.25,0.08,0.03),rough=0.3,metal=0.8)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.9, 0.9, 0.92),rough=0.14,metal=1.0)
