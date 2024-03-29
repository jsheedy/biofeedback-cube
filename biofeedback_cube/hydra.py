from collections import deque, defaultdict
from dataclasses import dataclass, field
from typing import Dict

import logging
import pickle
import time

from .config import HYDRA_STATE_FILE
from .modes import Modes


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

    modes: Dict[Modes, bool] = field(default_factory=lambda: {Modes.PLASMA3: None, Modes.PUNYTY: None})

    shutdown: bool = False
    last_update: float = 0

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name not in ('last_update',):
            self.last_update = time.time() - t0

    def fresh(self, t):
        """ return boolean whether hydra has been updated recently """
        dt = t - self.last_update
        return dt < .10

    def zero(self):
        for char in map(chr, range(97, 97 + 26)):
            try:
                setattr(self, char, 0.5)
            except AttributeError:
                pass
        self.e = 1.0  # brightness
        self.h = 0.0  # rotation


def save_hydra():
    hydra.shutdown = False
    logger.info(f'dumping hydra state to {HYDRA_STATE_FILE}')
    try:
        with open(HYDRA_STATE_FILE, 'wb') as f:
            pickle.dump(hydra, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        logger.exception(f'unable to save {HYDRA_STATE_FILE}')


try:
    with open(HYDRA_STATE_FILE, 'rb') as f:
        hydra = pickle.load(f)
        logger.warning(f'loading hydra state {hydra}')
except Exception:
    logger.exception(f'unable to initialize hydra with {HYDRA_STATE_FILE}')
    hydra = Hydra()
