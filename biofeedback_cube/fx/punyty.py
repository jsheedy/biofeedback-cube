import math

import numpy as np
from punyty.vector import Vector3
from punyty.objects import Cube, Tetrahedron, Octahedron, Dodecahedron
from punyty.renderers import ArrayRenderer
from punyty.scene import Scene

from ..hydra import hydra
from ..utils import sin, cos


scene = Scene()

objects = (
    Tetrahedron(color=Vector3(1, 0.8, 0.7), position=Vector3(-.35, 0, 1.3)),
    Cube(color=Vector3(1, 0.8, 0.7), position=Vector3(-.35, 0, 1.3)),
    Octahedron(color=Vector3(1, 0.8, 0.7), position=Vector3(-.35, 0, 1.3)),
    # Dodecahedron(color=Vector3(1, 0.8, 0.7), position=Vector3(-.35, 0, 1.3))
)

cache = {}


def get_target_array(grid, cache_key='target_array'):
    if cache_key in cache:
        return cache.get(cache_key)

    h, w, c = grid.shape
    s = max((h, w))
    ta = np.zeros((s, s, c), dtype=np.float32)
    cache[cache_key] = ta
    return ta


def get_renderer(target_array, cache_key='renderer'):
    if cache_key in cache:
        return cache.get(cache_key)

    renderer = ArrayRenderer(
        target_array=target_array,
        draw_edges=False,
        draw_wireframe=False,
        draw_polys=True
    )
    cache[cache_key] = renderer
    return renderer


def punyty(grid, t):
    target_array = get_target_array(grid)
    renderer = get_renderer(target_array)

    idx = int(hydra.g * (len(objects) - 1))
    obj = objects[idx]
    obj.position = Vector3(6 * (hydra.x - .35), 6 * (0.5-hydra.y), 0.05 + 20 * hydra.i)
    if hydra.f < 0.2:
        obj.rotate(Vector3(-3+hydra.a*6, -3+hydra.b*6, -3+hydra.c*6))
        obj.color = Vector3(hydra.a, hydra.b, hydra.c)
    else:
        obj.rotate(Vector3(math.sin(.9*t), math.sin(0.63*t), math.cos(0.85*t)))
        color = Vector3(sin(.1*t + 1), .1 + sin(0.08*t), cos(0.1515*t))
        obj.color = color

    scene.objects.clear()
    scene.add_object(obj)

    renderer.render(scene)

    grid_w = grid.shape[1]
    target_w = target_array.shape[1]
    xi = np.linspace(0, target_w, grid_w, endpoint=False, dtype=np.int32)
    dst = target_array[:, xi]
    mask = dst > 0
    grid[mask] = dst[mask]