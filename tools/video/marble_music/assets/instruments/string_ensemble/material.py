"""string_ensemble materials: body = cello; v_orange / v_brown = violin / viola"""
def shared(C):
    d = {
    'ebony': C.mat('se_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5), 'dark': C.mat('se_dark',(0.03,0.012,0.005),rough=0.6),
    'steel': C.mat('se_steel',(0.8,0.8,0.78),rough=0.25,metal=1.0), 'pale': C.mat('se_pale',(0.85,0.74,0.55),rough=0.4),
    'stick': C.add_wood(C.mat('se_stick',(0.2,0.07,0.02),rough=0.3,coat=0.6),(0.12,0.04,0.01),(0.3,0.11,0.03),scale=12.0),
    'hair': C.mat('se_hair',(0.92,0.9,0.84),rough=0.6), 'pearl': C.mat('se_pearl',(0.85,0.88,0.9),rough=0.1,coat=1.0)}
    d['v_orange'] = C.add_wood(C.mat('se_vo',(0.62,0.15,0.02),rough=0.25,coat=0.85),(0.45,0.08,0.01),(0.75,0.2,0.03),scale=6.0)
    d['v_brown'] = C.add_wood(C.mat('se_vb',(0.12,0.045,0.015),rough=0.25,coat=0.85),(0.07,0.025,0.008),(0.18,0.07,0.025),scale=6.0)
    d['velvet'] = C.mat('se_velvet',(0.4,0.02,0.04),rough=0.95); d['gold'] = C.mat('se_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0)
    return d

def body(C, name, j, note, variant):
    return C.add_wood(C.mat(name,(0.28, 0.05, 0.015),rough=0.25,coat=0.85),(0.18, 0.03, 0.01),(0.36, 0.07, 0.02),scale=6.0)
