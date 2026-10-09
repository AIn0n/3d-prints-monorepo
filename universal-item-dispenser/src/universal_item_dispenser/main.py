# %%
from copy import deepcopy

from build123d import *
from ocp_vscode import show

# %%


def universal_item_dispenser(size: int):
    base_size_x = 10
    base_size_y = 10
    circle_r = 0.25
    n = 100
    base_z = 1
    total_z = 20
    total_rounding = 1

    obj_x = 6
    obj_y = 8
    obj_z = 2

    finger_hole_height = 5
    finger_hole_width = 3

    lid_height = 2

    with BuildPart() as dispenser:
        with BuildSketch() as solid_walls:
            RectangleRounded(base_size_x, base_size_y, total_rounding)
        extrude(solid_walls.sketch, amount=total_z)

        locs = [solid_walls.wire().position_at(i / n) for i in range(n)]
        with BuildSketch() as circles:
            with Locations(locs):
                Circle(circle_r)
        extrude(circles.sketch, amount=total_z)

        topf = dispenser.faces().sort_by(Axis.Z)[-1]
        start = topf.vertices().group_by(Axis.X)[0][0]
        with BuildSketch(topf) as hole:
            with Locations((start.X + circle_r, 0, start.Z)):
                Rectangle(obj_x, obj_y, align=(Align.MIN, Align.CENTER))

        extrude(hole.sketch, amount=-total_z + base_z, mode=Mode.SUBTRACT)

        front_inner_wall = dispenser.faces().filter_by(GeomType.PLANE).sort_by(Axis.X)[0]
        plane_inner_wall = Plane(front_inner_wall, z_dir=(-1, 0, 0))
        plane_inner_wall = plane_inner_wall.shift_origin(
            front_inner_wall.edges().sort_by(Axis.Z)[0].center()
        )
        with BuildSketch(plane_inner_wall) as slot:
            RectangleRounded(obj_y, obj_z, radius=0.5, align=(Align.CENTER, Align.MIN))
            RectangleRounded(
                finger_hole_width,
                finger_hole_height,
                radius=finger_hole_width / 2 - 0.01,
                align=(Align.CENTER, Align.MIN),
            )

        extrude(slot.sketch, amount=-5, mode=Mode.SUBTRACT)

        bottom_face = dispenser.faces().sort_by(Axis.Z)[0]
        with BuildSketch(bottom_face.offset(- total_z - 4)) as lid_base:
            RectangleRounded(bottom_face.width, bottom_face.length, total_rounding)

        extrude(lid_base.sketch, amount=lid_height)
        chamfer(dispenser.edges().group_by(Axis.Z)[-1], length=0.5)

        

    return dispenser.part



show(universal_item_dispenser(4))

# %%

length, thickness = 80.0, 10.0

with BuildPart() as ex19:
    with BuildSketch() as ex19_sk:
        RegularPolygon(radius=length / 2, side_count=7)
    extrude(amount=thickness)
    topf = ex19.faces().sort_by(Axis.Z)[-1]
    vtx = topf.vertices().group_by(Axis.X)[-1][0]
    vtx2Axis = Axis((0, 0, 0), (-1, -0.5, 0))
    vtx2 = topf.vertices().sort_by(vtx2Axis)[-1]
    with BuildSketch(topf) as ex19_sk2:
        with Locations((vtx.X, vtx.Y), (vtx2.X, vtx2.Y)):
            Circle(radius=length / 8)
    extrude(amount=-thickness, mode=Mode.SUBTRACT)

show(ex19.part)
