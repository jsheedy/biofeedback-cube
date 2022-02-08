def fire(grid, t):
    grid[:, ::3, :] = 0.0, 1.0, 0.0
