"""woodblock_castanets materials"""
def shared(C):
    return {'dark': C.mat('wc_dark',(0.01,0.004,0.002),rough=0.7), 'shell': C.add_wood(C.mat('wc_shell',(0.035, 0.016, 0.008),rough=0.2,coat=1.0),(0.02, 0.009, 0.004),(0.07, 0.035, 0.015),scale=5.0), 'cord': C.mat('wc_cord',(0.7,0.03,0.03),rough=0.6)}
def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.16,0.04,0.015),rough=0.2,coat=1.0),(0.1,0.025,0.01),(0.24,0.07,0.03),scale=5.0)
