"""bells_castanets materials"""
def shared(C):
    return {'tube': C.mat('bc_tube',(0.95,0.68,0.26),rough=0.12,metal=1.0), 'cap': C.mat('bc_cap',(0.80,0.48,0.14),rough=0.08,metal=1.0),
            'dark': C.mat('bc_dark',(0.03,0.025,0.02),rough=0.35,coat=0.6),
            'shell': C.add_wood(C.mat('bc_shell',(0.32,0.09,0.04),rough=0.3,coat=0.7),(0.20,0.05,0.02),(0.50,0.18,0.07)),
            'cord': C.mat('bc_cord',(0.75,0.03,0.03),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.93,0.66,0.27),rough=0.12,metal=1.0)
