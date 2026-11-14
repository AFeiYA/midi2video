"""finale materials"""
def shared(C):
    st = C.mat('fin_star',(1.0,0.72,0.25),rough=0.15,metal=1.0); b = st.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (1.0,0.7,0.3,1); b.inputs['Emission Strength'].default_value = 0.6
    return {'star': st, 'ribbon': C.mat('fin_ribbon',(0.7,0.02,0.04),rough=0.35,coat=0.6),
            'bell': C.mat('fin_bell',(0.95,0.7,0.3),rough=0.1,metal=1.0), 'dark': C.mat('fin_dark',(0.02,0.015,0.01),rough=0.5)}
def body(C, name, j, note, variant):
    return C.mat(name,(1.0,0.76,0.32),rough=0.08,metal=1.0)
