"""flute v8: darker lacquered rosewood body (hit surface); warm matte cream rings/bell/foot; dark bore/holes."""
def shared(C):
    # Warm bone/cream, not glossy white — bloom was blowing the previous ivory.
    ivory = C.mat('fl8_ivory', (0.62, 0.50, 0.32), rough=0.48, coat=0.12, coat_rough=0.2)
    return {
        'ivory': ivory,
        'dark':  C.mat('fl8_dark', (0.03, 0.02, 0.012), rough=0.8),
    }

def body(C, name, j, note, variant):
    # Richer reddish-brown, closer to the reference recorder; less coat so it does not chalk out.
    m = C.mat(name, (0.28, 0.11, 0.045), rough=0.35, coat=0.22, coat_rough=0.12)
    C.add_wood(m, (0.18, 0.06, 0.025), (0.42, 0.18, 0.07), scale=8.0)
    return m
