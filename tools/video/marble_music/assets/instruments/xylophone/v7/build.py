"""xylophone v7: the coloured bar itself is the striker (slim, rounded), not a thick board with a frame behind it.
Top face flush with the contact plane at z=+0.045. No felt rail, no birch frame."""
def build(C, variant=None):
    # 0.62 x 0.10 x 0.09: a bar the marble can sit on, not a 0.30-deep plank filling the slab
    bar = C.prim('cube', 0, scale=(0.62, 0.11, 0.09), bevel=0.02)
    return [bar]
