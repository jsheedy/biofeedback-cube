from collections import deque, defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Dict

import logging
import pickle
import time

from .config import HYDRA_STATE_FILE, HYDRA_STATE_SAVE_DIR
from .modes import Modes


logger = logging.getLogger(__name__)
t0 = time.time()
hydra = None

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


def save_hydra(default=True):
    if default is True:
        fname = HYDRA_STATE_FILE
    else:
        dest_dir = Path(HYDRA_STATE_SAVE_DIR)
        dest_dir.mkdir(parents=True, exist_ok=True)

        name = f"cube-{datetime.now().isoformat(timespec='seconds')}.state"
        fname = dest_dir / Path(name)

    hydra.shutdown = False
    logger.info(f'dumping hydra state to {fname}')
    try:
        with open(fname, 'wb') as f:
            pickle.dump(hydra, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception:
        logger.exception(f'unable to save {fname}')

def load_hydra(fname=None):
    global hydra
    if fname is None:
        fname = HYDRA_STATE_FILE

    try:
        with open(fname, 'rb') as f:
            hydra = pickle.load(f)
            logger.warning(f'loading hydra state {hydra}')
    except Exception:
        logger.exception(f'unable to initialize hydra with {fname}')
        hydra = Hydra()

def load_saved_hydra(value):
    states = list(Path(HYDRA_STATE_SAVE_DIR).glob('*.state'))
    index = int(value * (len(states) - 1))
    fname = states[index]
    load_hydra(fname)

load_hydra()