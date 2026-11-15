"""voice_oohs materials (red = ON-AIR lamp, emissive)"""
def shared(C):
    r = C.mat('vo_red',(0.8,0.05,0.04),rough=0.3); b = r.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (1.0,0.12,0.06,1); b.inputs['Emission Strength'].default_value = 2.5
    return {'grille': C.mat('vo_grille',(0.03,0.03,0.035),rough=0.5,metal=0.5), 'gold': C.mat('vo_gold',(0.95,0.72,0.35),rough=0.2,metal=1.0),
            'black': C.mat('vo_black',(0.02,0.02,0.022),rough=0.35,coat=0.5), 'red': r}
def body(C, name, j, note, variant):
    return C.mat(name,(0.9,0.9,0.92),rough=0.07,metal=1.0)
