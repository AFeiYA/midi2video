"""tenor_sax materials"""
def shared(C):
    return {'pearl': C.mat('tenor_sax_pearl',(0.9,0.9,0.86),rough=0.1,coat=1.0), 'keys': C.mat('tenor_sax_keys',(0.92, 0.64, 0.24),rough=0.16,metal=1.0),
            'dark': C.mat('tenor_sax_dark',(0.02,0.015,0.01),rough=0.6), 'mouth': C.mat('tenor_sax_mouth',(0.015,0.015,0.015),rough=0.25,coat=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.02, 0.02, 0.022),rough=0.18,metal=0.0,coat=1.0)
