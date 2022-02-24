import os

HEIGHT = 68
WIDTH = 8
# aspect ratio of device is
# 5 1/8" / 130.175mm horizontal spacing (measured)
# 17mm vertical spacing per adafruit,
ASPECT = 130.175 / 17

HYDRA_STATE_FILE = '/srv/hydra/hydra.state'
# HYDRA_STATE_FILE = f'{os.getenv("HOME")}/.hydra.state'
