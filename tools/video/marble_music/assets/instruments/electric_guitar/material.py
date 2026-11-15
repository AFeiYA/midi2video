"""electric_guitar materials"""
def shared(C):
    return {'nickel': C.mat('eg_nickel',(0.8,0.8,0.78),rough=0.25,metal=1.0), 'guard': C.mat('eg_guard',(0.92,0.9,0.86),rough=0.3,coat=0.5),
            'maple': C.add_wood(C.mat('eg_maple',(0.8,0.6,0.32),rough=0.3,coat=0.7),(0.74,0.54,0.28),(0.9,0.72,0.42),scale=7.0),
            'dark': C.mat('eg_dark',(0.02,0.015,0.01),rough=0.5), 'chrome': C.mat('eg_chrome',(0.9,0.9,0.92),rough=0.08,metal=1.0)}
def body(C, name, j, note, variant):
    return C.mat(name,(0.12,0.42,0.75),rough=0.15,coat=1.0)
