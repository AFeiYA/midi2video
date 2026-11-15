"""jb_vibraphone materials (body = the struck bar; neighbour bars use the 'chrome' slot in a satin finish)"""
def shared(C):
    return {'cord': C.mat('jv_cord',(0.35,0.03,0.05),rough=0.8), 'resonator': C.mat('jv_res',(0.9,0.66,0.28),rough=0.22,metal=1.0),
            'dark': C.mat('jv_dark',(0.02,0.02,0.022),rough=0.45), 'chrome': C.mat('jv_alu2',(0.78,0.8,0.84),rough=0.28,metal=1.0,aniso=0.5)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.82,0.84,0.88),rough=0.24,metal=1.0,aniso=0.6)
