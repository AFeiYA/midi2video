"""electric_grand materials"""
def shared(C):
    return {'case': C.mat('eg_case',(0.82,0.80,0.76),rough=0.15,coat=1.0), 'chrome': C.mat('eg_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0),
            'red': C.mat('eg_red',(0.7,0.02,0.02),rough=0.4), 'dark': C.mat('eg_dark',(0.01,0.01,0.01),rough=0.6)}
def body(C, name, j, note, variant):
    if variant == 'black': return C.mat(name,(0.02,0.02,0.022),rough=0.2,coat=0.8)
    return C.mat(name,(0.90,0.90,0.88),rough=0.2,coat=0.5)
