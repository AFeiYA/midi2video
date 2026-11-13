"""tubular bells v5 materials."""
def shared(C):
    return {'tube': C.mat('tb5_tube',(0.88,0.6,0.22),rough=0.14,metal=1.0), 'cap': C.mat('tb5_cap',(0.75,0.45,0.14),rough=0.1,metal=1.0),
            'dark': C.mat('tb5_dark',(0.05,0.03,0.01),rough=0.6,metal=0.5), 'cord': C.mat('tb5_cord',(0.15,0.12,0.1),rough=0.8)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.86,0.6,0.25),rough=0.16,metal=1.0)
