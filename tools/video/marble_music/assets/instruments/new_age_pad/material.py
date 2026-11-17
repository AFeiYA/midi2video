"""new_age_pad materials"""
def shared(C):
    return {'gold': C.mat('na_gold',(1.0, 0.75, 0.35),rough=0.12,metal=1.0), 'glass': C.mat('na_glass',(0.8,0.85,1.0),rough=0.0,trans=1.0,ior=1.3), 'core': (lambda m: (m.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].__setattr__('default_value', (0.45,0.15,1.0,1)), m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].__setattr__('default_value', 3.5), m)[-1])(C.mat('na_core',(0.2, 0.05, 0.5),rough=0.3)), 'star': (lambda m: (m.node_tree.nodes['Principled BSDF'].inputs['Emission Color'].__setattr__('default_value', (1.0,0.75,0.3,1)), m.node_tree.nodes['Principled BSDF'].inputs['Emission Strength'].__setattr__('default_value', 4.0), m)[-1])(C.mat('na_star',(1.0, 0.75, 0.3),rough=0.3)), 'tassel': C.mat('na_tassel',(0.45,0.15,0.6),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.8,0.7,0.95),rough=0.15,coat=1.0)
