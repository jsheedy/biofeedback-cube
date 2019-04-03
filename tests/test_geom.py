from biofeedback_cube import geom


def test_line_intersect():
    points = (0, 0, 1, 1, 1, 0, 0, 1)
    assert geom.line_intersect(*points) == (0.5, 0.5)


def test_line_not_intersect():
    points = (0, 0, .5, .5, 1, 0, 1, 1)
    assert not geom.line_intersect(*points)


def test_point_in_uv():
    assert geom.point_in_uv(.5, .5)


def test_line_intersects_uv_twice():
    intersection = geom.line_intersects_uv(0.5, -2, 0.5, 2)
    assert len(intersection) == 2
    assert (0.5, 0) in intersection
    assert (0.5, 1) in intersection

def test_line_intersects_uv_twice():
    points = (0.5, 1.5, -0.5, -1.5)
    intersection = geom.line_intersects_uv(*points)
    assert len(intersection) == 2


def test_line_intersects_uv_once():
    intersection = geom.line_intersects_uv(0.5, 0.5, 0.5, 2)
    assert len(intersection) == 1
    assert (0.5, 1) in intersection


def test_line_intersects_uv_none():
    intersection = geom.line_intersects_uv(0.1, 0.1, 0.9, 0.9)
    assert len(intersection) == 0