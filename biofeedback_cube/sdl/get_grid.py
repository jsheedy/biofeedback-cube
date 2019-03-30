import numpy as np

def keyframes(cols, rows):
    times = np.linspace(0,1, 5)
    frames = np.zeros((cols, rows, 3, 5))

    frames[:,:,0,0] = 1
    frames[:,:(rows//2),1,1] = 1
    frames[:,(rows//2):,2,2] = 1
    frames[:,:,:,3] = 1
    frames[:,:,1:2,4] = 1
    return times, frames

def get_grid(cols, rows, t, joystick):
    # grid = joystick.y*np.random.random((cols,rows,3)) # np.mgrid[100:100] # ds['hgt'][t,state.l]

    times, frames = keyframes(cols, rows)
    idx = int(4*joystick.y)
    grid1 = frames[:,:,:,idx]
    grid2 = frames[:,:,:,idx+1]
    t1 = times[idx]
    t2 = times[idx+1]

    dt = 4 * (joystick.y - idx/4)
    grid = grid1 * (1-dt) + grid2 * (dt)
    print(idx, t1, t2, joystick.y, dt)
    return grid
