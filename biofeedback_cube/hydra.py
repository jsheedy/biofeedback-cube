from dataclasses import dataclass, field
import time
from typing import Set, Tuple

from .osc import update_client


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

    a: float = 0.5
    b: float = 0.5
    c: float = 0.5
    d: float = 0.5
    e: float = 0.5
    f: float = 0.5
    g: float = 0.5

    mode: int = 9
    shutdown: bool = False
    last_update: float = 0


    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name not in ('last_update', 'pulse'):
            self.last_update = time.time() - t0

        for client in self.clients:
            update_client(client, name, value)

hydra = Hydra()
