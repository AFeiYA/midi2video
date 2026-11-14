"""pixel8bit materials: glossy candy-coloured blocks, emissive pixels."""
import colorsys
PAL = [0.0, 0.08, 0.15, 0.33, 0.5, 0.62, 0.8]
def shared(C):
    g = C.mat('px_glow',(0.2,0.95,1.0),rough=0.3); b = g.node_tree.nodes['Principled BSDF']
    b.inputs['Emission Color'].default_value = (0.25,0.95,1.0,1); b.inputs['Emission Strength'].default_value = 6.0
    return {'plate': C.mat('px_plate',(0.03,0.03,0.045),rough=0.35,coat=0.5), 'glow': g, 'accent': C.mat('px_accent',(0.9,0.9,0.9),rough=0.25,coat=0.6)}
def body(C, name, j, note, variant):
    r, g, b = colorsys.hsv_to_rgb(PAL[j % len(PAL)], 1.0, 0.45)
    return C.mat(name,(r,g,b),rough=0.2,coat=0.8)
