"""brass_section materials"""
def shared(C):
    return {'brass': C.mat('bs_brass',(0.92, 0.64, 0.24),rough=0.15,metal=1.0), 'dark': C.mat('bs_dark',(0.02,0.015,0.01),rough=0.6),
            'paper': C.mat('bs_paper',(0.9,0.88,0.82),rough=0.7), 'ink': C.mat('bs_ink',(0.02,0.02,0.02),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.92, 0.64, 0.24),rough=0.12,metal=1.0)
