"""jb_xylophone materials: body by pitch class; icon bars alternate two rainbow ramps along x (object-space gradient)"""
def _ramp(C, name, offset):
    m = C.mat(name,(1,1,1),rough=0.35,coat=0.5); nt = m.node_tree; b = nt.nodes['Principled BSDF']
    tc = nt.nodes.new('ShaderNodeTexCoord'); sep = nt.nodes.new('ShaderNodeSeparateXYZ'); mp = nt.nodes.new('ShaderNodeMapRange')
    mp.inputs['From Min'].default_value = -0.46; mp.inputs['From Max'].default_value = 0.46
    mp.inputs['To Min'].default_value = 0.0; mp.inputs['To Max'].default_value = 0.8
    hsv = nt.nodes.new('ShaderNodeCombineColor'); hsv.mode = 'HSV'; hsv.inputs[1].default_value = 0.85; hsv.inputs[2].default_value = 0.6
    L = nt.links.new; L(tc.outputs['Object'], sep.inputs[0]); L(sep.outputs[0], mp.inputs['Value']); L(mp.outputs[0], hsv.inputs[0]); L(hsv.outputs[0], b.inputs['Base Color'])
    return m
def shared(C):
    return {'maple': C.add_wood(C.mat('jx_maple',(0.7,0.5,0.28),rough=0.4,coat=0.3),(0.62,0.42,0.22),(0.82,0.62,0.38),scale=7.0),
            'rainbow0': _ramp(C,'jx_rb0',0), 'rainbow1': _ramp(C,'jx_rb1',0), 'silver': C.mat('jx_silver',(0.85,0.85,0.88),rough=0.2,metal=1.0),
            'red': C.mat('jx_red',(0.7,0.04,0.04),rough=0.35,coat=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,C.pitch_rgb(note),rough=0.32,coat=0.6)
