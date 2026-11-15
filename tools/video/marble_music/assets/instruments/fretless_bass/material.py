"""fretless_bass materials (line = the white fret-position lines on the fretless board)"""
def shared(C):
    m = C.mat('fb_tort',(0.25,0.08,0.02),rough=0.2,coat=0.8); C.add_wood(m,(0.06,0.02,0.005),(0.45,0.16,0.04),scale=14.0)
    return {'steel': C.mat('fb_steel',(0.75,0.75,0.74),rough=0.3,metal=1.0), 'tort': m,
            'ebony': C.mat('fb_ebony',(0.012,0.01,0.01),rough=0.3,coat=0.5), 'line': C.mat('fb_line',(0.9,0.9,0.86),rough=0.3),
            'chrome': C.mat('fb_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.18,0.04,0.34),rough=0.15,coat=1.0)
