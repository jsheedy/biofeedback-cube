from dataclasses import dataclass, field
import time
from typing import Set, Tuple

from .modes import Modes
from .osc import update_client, update_client_xy


t0 = time.time()

@dataclass
class Hydra():
    clients: Set[Tuple] = field(default_factory=set)

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

    mode: Modes = Modes.MARIO.value
    shutdown: bool = False
    last_update: float = 0

    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name not in ('last_update', 'pulse'):
            self.last_update = time.time() - t0

        for client in self.clients:
            if name in ('x', 'y'):
                update_client_xy(client, self.x, self.y)
            else:
                update_client(client, name, value)

    def fresh(self, t):
        """ return boolean whether hydra has been updated recently """
        dt = t - self.last_update
        return dt < .3

hydra = Hydra()
