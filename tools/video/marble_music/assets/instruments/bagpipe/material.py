"""bagpipe materials: Royal-Stewart-ish procedural tartan."""
def tartan(C):
    m = C.mat('bp_tartan',(0.6,0.03,0.03),rough=0.85); nt = m.node_tree; b = nt.nodes['Principled BSDF']; L = nt.links.new
    tc = nt.nodes.new('ShaderNodeTexCoord'); sp = nt.nodes.new('ShaderNodeSeparateXYZ'); L(tc.outputs['Object'], sp.inputs[0])
    def band(sock, freq, width):
        mu = nt.nodes.new('ShaderNodeMath'); mu.operation = 'MULTIPLY'; mu.inputs[1].default_value = freq; L(sock, mu.inputs[0])
        fr = nt.nodes.new('ShaderNodeMath'); fr.operation = 'FRACT'; L(mu.outputs[0], fr.inputs[0])
        lt = nt.nodes.new('ShaderNodeMath'); lt.operation = 'LESS_THAN'; lt.inputs[1].default_value = width; L(fr.outputs[0], lt.inputs[0]); return lt.outputs[0]
    def mx(fac, c1sock, c2):
        n = nt.nodes.new('ShaderNodeMix'); n.data_type = 'RGBA'; L(fac, n.inputs['Factor'])
        if isinstance(c1sock, tuple): n.inputs[6].default_value = (*c1sock, 1)
        else: L(c1sock, n.inputs[6])
        n.inputs[7].default_value = (*c2, 1); return n.outputs[2]
    bx = band(sp.outputs['X'], 7.0, 0.32); bz = band(sp.outputs['Z'], 7.0, 0.32)
    both = nt.nodes.new('ShaderNodeMath'); both.operation = 'MULTIPLY'; L(bx, both.inputs[0]); L(bz, both.inputs[1])
    any_ = nt.nodes.new('ShaderNodeMath'); any_.operation = 'MAXIMUM'; L(bx, any_.inputs[0]); L(bz, any_.inputs[1])
    c = mx(any_.outputs[0], (0.62,0.03,0.03), (0.05,0.16,0.07))       # red ground, green bands
    c = mx(both.outputs[0], c, (0.01,0.03,0.08))                      # navy where bands cross
    yx = band(sp.outputs['X'], 7.0, 0.04); yz = band(sp.outputs['Z'], 7.0, 0.04)
    y = nt.nodes.new('ShaderNodeMath'); y.operation = 'MAXIMUM'; L(yx, y.inputs[0]); L(yz, y.inputs[1])
    c = mx(y.outputs[0], c, (0.85,0.7,0.1))                           # thin yellow over-check
    L(c, b.inputs['Base Color']); return m
def shared(C):
    return {'tartan': tartan(C), 'ivory': C.mat('bp_ivory',(0.92,0.88,0.78),rough=0.25,coat=0.5),
            'pipe': C.mat('bp_pipe',(0.025,0.02,0.018),rough=0.25,coat=0.8), 'cord': C.mat('bp_cord',(0.7,0.04,0.04),rough=0.6)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.03,0.025,0.022),rough=0.2,coat=0.9)
