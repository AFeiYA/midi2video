"""koto materials"""
def shared(C):
    return {'board': C.add_wood(C.mat('ko_board',(0.05,0.02,0.007),rough=0.5,coat=0.0),(0.03,0.011,0.004),(0.11,0.045,0.014),scale=3.0,rings=1.2),
            'string': C.mat('ko_string',(0.4,0.32,0.15),rough=0.5), 'bridge': C.mat('ko_bridge',(0.98,0.96,0.9),rough=0.2,coat=0.5),
            'trim': C.mat('ko_trim',(0.92,0.7,0.3),rough=0.15,metal=1.0)}
def body(C, name, j, note, variant):
    m = C.mat(name,(0.08,0.025,0.015),rough=0.3,coat=0.8); return C.add_wood(m,(0.04,0.012,0.008),(0.16,0.05,0.025))
