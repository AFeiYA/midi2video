"""guitar materials: shared(C) -> role->material for non-flash slots; body(C,name,j,note,variant) -> per-key struck material."""
def shared(C):
    m = C.mat('gt_bridge',(0.12,0.05,0.03),rough=0.4,coat=0.3)
    return {'strings': C.mat('gt_str',(0.95,0.75,0.42),rough=0.12,metal=1.0), 'bridge': C.add_wood(m,(0.07,0.03,0.015),(0.2,0.09,0.04)),
            'dark': C.mat('gt_dark',(0.01,0.008,0.006),rough=0.9), 'bone': C.mat('gt_bone',(0.9,0.87,0.78),rough=0.4)}
def body(C, name, j, note, variant):
    m = C.mat(name,(0.8,0.6,0.35),rough=0.3,coat=0.8); return C.add_wood(m,(0.66,0.47,0.24),(0.90,0.74,0.48),scale=9.0)
