from dataclasses import dataclass, field

import logging
from pathlib import Path
import pickle
import time
from typing import Set, Tuple

from .config import HYDRA_STATE_FILE
from .modes import Modes
from .osc import hydra_callback


logger = logging.getLogger(__name__)
t0 = time.time()

@dataclass
class Hydra():
    x: float = 0.5
    y: float = 0.5
    z: float = 0.5

    xyz_x: float = 0.5
    xyz_y: float = 0.5
    xyz_z: float = 0.5

    a: float = 0.9
    b: float = 0.3
    c: float = 0.1
    d: float = 0.5
    e: float = 0.5
    f: float = 0.5
    g: float = 0.5
    h: float = 0.5
    i: float = 0.5
    j: float = 0.5
    k: float = 0.5
    l: float = 0.5
    m: float = 0.5
    n: float = 0.5
    o: float = 0.5
    p: float = 0.5
    q: float = 0.5

    mode: Modes = Modes.PLASMA
    shutdown: bool = False
    last_update: float = 0

    dirty = False

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name not in ('last_update', 'dirty'):
            self.dirty = True
            self.last_update = time.time() - t0

    def fresh(self, t):
        """ return boolean whether hydra has been updated recently """
        dt = t - self.last_update
        return dt < .3

def save_hydra():
    if not hydra.dirty:
        return
    hydra.dirty = False
    logger.info(f'dumping hydra state to {HYDRA_STATE_FILE}')
    with open(HYDRA_STATE_FILE, 'wb') as f:
        pickle.dump(hydra, f, protocol=pickle.HIGHEST_PROTOCOL)


if Path(HYDRA_STATE_FILE).is_file():
    with open(HYDRA_STATE_FILE, 'rb') as f:
        hydra = pickle.load(f)
        logger.warning(f'loading hydra state {hydra}')
else:
    hydra = Hydra()
