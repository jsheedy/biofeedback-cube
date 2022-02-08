import math

from biofeedback_cube.hydra import hydra

from punyty.vector import Vector3
from punyty.objects import Cube
from punyty.renderers import ArrayRenderer
from punyty.scene import Scene

scene = Scene()
cube = Cube(color=Vector3(1, 0.8, 0.7), position=Vector3(-.35, 0, 1.3))
scene.add_object(cube)


def punyty(buffer, t):
    renderer = ArrayRenderer(
        target_array=buffer,
        draw_edges=False,
        draw_wireframe=False,
        draw_polys=True
    )
    if hydra.f < 0.2:
        cube.rotate(Vector3(-3+hydra.a*6, -3+hydra.b*6, -3+hydra.c*6))
        cube.color = Vector3(hydra.a, hydra.b, hydra.c)
    else:
        cube.rotate(Vector3(math.sin(.2*t), math.sin(0.23*t), math.cos(0.25*t)))
        color = Vector3(math.sin(.1*t), math.sin(0.08*t), math.cos(0.1515*t))
        cube.color = color

    renderer.render(scene)
