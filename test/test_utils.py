import numpy as np
from biofeedback_cube import utils

def test_decimate():
    x = np.linspace(0,8,4)
    y = np.linspace(0,1,4)
    z = np.linspace(0,1,4)
    x = np.meshgrid(x,y,z)
    xp = utils.decimate(x)
    assert xp[0, 0, 0] == 0.0