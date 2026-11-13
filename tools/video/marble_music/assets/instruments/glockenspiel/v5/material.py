"""glockenspiel v5 materials (v4 + graded steel bars). glockenspiel v4: polished steel with a slightly darker tone (reads against the pale wall), red lacquer rails, brass screws."""
def shared(C):
    return {'bars': C.mat('gl5_bars',(0.70,0.72,0.76),rough=0.08,metal=1.0), 'wood': C.mat('gl4_rail',(0.62,0.03,0.025),rough=0.5), 'screw': C.mat('gl4_screw',(0.9,0.65,0.25),rough=0.15,metal=1.0),
            'felt': C.mat('gl4_felt',(0.5,0.03,0.04),rough=0.95)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.66,0.68,0.72),rough=0.06,metal=1.0)
