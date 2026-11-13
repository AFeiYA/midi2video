"""guitar v4 materials: amber->dark-brown sunburst top; bright nickel strings (also flash per key)."""
# strings are black-coated (non-metallic) so they stay dark under the studio reflectors; rails are matte red (a clearcoat mirrored the softbox and read grey)
def shared(C):
    m = C.mat('gt4_bridge',(0.06,0.025,0.012),rough=0.35,coat=0.4)
    return {'strings': C.mat('gt4_str',(0.012,0.012,0.014),rough=0.45), 'bridge': C.add_wood(m,(0.03,0.012,0.006),(0.11,0.05,0.022)),
            'dark': C.mat('gt4_dark',(0.006,0.004,0.003),rough=0.9), 'bone': C.mat('gt4_bone',(0.92,0.88,0.78),rough=0.35),
            'fret': C.mat('gt4_fret',(0.85,0.85,0.8),rough=0.15,metal=1.0)}
def body(C, name, j, note, variant):
    m = C.mat(name,(0.6,0.35,0.1),rough=0.35,coat=0.35,coat_rough=0.08)
    C.add_wood(m,(0.50,0.26,0.06),(0.78,0.50,0.16),scale=9.0)
    nt = m.node_tree; b = nt.nodes['Principled BSDF']
    wood = b.inputs['Base Color'].links[0].from_socket
    tc = nt.nodes.new('ShaderNodeTexCoord'); mp = nt.nodes.new('ShaderNodeMapping'); mp.inputs['Scale'].default_value = (3.0, 4.0, 1.0)
    gr = nt.nodes.new('ShaderNodeTexGradient'); gr.gradient_type = 'SPHERICAL'
    rp = nt.nodes.new('ShaderNodeValToRGB'); rp.color_ramp.elements[0].position = 0.0; rp.color_ramp.elements[0].color = (0.02,0.008,0.004,1)
    rp.color_ramp.elements[1].position = 0.55; rp.color_ramp.elements[1].color = (1,1,1,1)
    mx = nt.nodes.new('ShaderNodeMix'); mx.data_type = 'RGBA'; mx.blend_type = 'MULTIPLY'; mx.inputs['Factor'].default_value = 1.0
    L = nt.links.new
    L(tc.outputs['Object'], mp.inputs[0]); L(mp.outputs[0], gr.inputs[0]); L(gr.outputs['Fac'], rp.inputs[0])
    L(wood, mx.inputs[6]); L(rp.outputs['Color'], mx.inputs[7]); L(mx.outputs[2], b.inputs['Base Color'])
    return m
