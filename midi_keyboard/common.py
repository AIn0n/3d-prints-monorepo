from enum import Flag, auto
from itertools import accumulate
from math import atan2, degrees, floor, sqrt
from typing import Any, Callable, Sequence

from base_builders import GroupBuilder, ModelBuilder
from configuration import ConfigSchema
from solid2 import cube, cylinder, square


def floor_to_half(x):
    return floor(x * 2) / 2


OptionalCopyField = float | Callable[[float], float] | None


def resolve_optional_copy_field(arg: float, field: OptionalCopyField) -> float:
    if field is None:
        return arg
    if isinstance(field, float) or isinstance(field, int):
        return field
    return field(arg)


class StandBuilder(ModelBuilder):
    def __init__(self, conf: ConfigSchema):
        diameter = conf.stand_r_mm * 2
        self.r = conf.stand_r_mm
        self.h = conf.base_height_mm
        self.hole_r = conf.stand_screw_r_mm
        super().__init__(0, 0, 0, conf.stand_r_mm, conf.stand_r_mm, conf.base_height_mm)

    def _stand(self):
        return cylinder(h=self.h, r=self.r) - cylinder(h=self.h, r=self.hole_r)

    def build(self):
        return self._stand().translate([self.x, self.y, self.z])


class SlopeBuilder(ModelBuilder):
    def __init__(self, dx: float, dy: float, dz: float):
        super().__init__(0, 0, 0, dx, dy, dz)

    def _slope(self):
        sqr = square([self.dx, self.dy])
        rad_angle = atan2(self.dy, self.dz)
        angle = degrees(rad_angle)

        return sqr.linear_extrude(self.dz) - sqr.linear_extrude(
            sqrt(self.dx**2 + self.dy**2) * 1.5
        ).rotateX(-angle)

    def build(self):
        return self._slope().translate([self.x, self.y, self.z])


class SquareXPunchedSlopeBuilder(SlopeBuilder):
    def __init__(
        self,
        dx: float,
        dy: float,
        dz: float,
        distances: list[float],
        hole_dims: tuple[float, float],
    ) -> None:
        self.distances = distances
        self.hole_x, self.hole_y = hole_dims
        super().__init__(dx, dy, dz)

    def build(self) -> Any:
        model = super().build()
        hole = cube([self.hole_x, self.hole_y, self.dz])
        for dist in accumulate(self.distances):
            model -= hole.translateX(dist).translateZ(self.z)
        return model


class CubeBuilder(ModelBuilder):
    def __init__(self, dx, dy, dz) -> None:
        super().__init__(0, 0, 0, dx, dy, dz)

    def copy_and_modify(
        self,
        new_x: OptionalCopyField = None,
        new_y: OptionalCopyField = None,
        new_z: OptionalCopyField = None,
        new_dx: OptionalCopyField = None,
        new_dy: OptionalCopyField = None,
        new_dz: OptionalCopyField = None,
    ) -> CubeBuilder:
        copy = CubeBuilder(
            resolve_optional_copy_field(self.dx, new_dx),
            resolve_optional_copy_field(self.dy, new_dy),
            resolve_optional_copy_field(self.dz, new_dz),
        )
        copy.move(
            [
                resolve_optional_copy_field(self.x, new_x),
                resolve_optional_copy_field(self.y, new_y),
                resolve_optional_copy_field(self.z, new_z),
            ]
        )
        return copy

    def build(self):
        return cube([self.dx, self.dy, self.dz]).translate([self.x, self.y, self.z])


class KeyRowBuilder(ModelBuilder):
    def __init__(
        self,
        width: float,
        len_: float,
        x_key_offsets: list[float],
        y_offset: float,
        conf: ConfigSchema,
    ):
        self.conf = conf
        self.x_key_offsets = x_key_offsets
        self.y_offset = y_offset
        super().__init__(0, 0, 0, width, len_, self.conf.mount_plate_width)

    def to_cube(self) -> CubeBuilder:
        cube = CubeBuilder(self.dx, self.dy, self.dz)
        cube.move([self.x, self.y, self.z])
        return cube

    def generate_key_row(self):
        mx_hole = square([self.conf.mount_u, self.conf.mount_u]).translateY(
            self.y_offset
        )
        mounting_plate = square([self.dx, self.dy])

        for sep in accumulate(self.x_key_offsets):
            mounting_plate -= mx_hole.translateX(sep)

        return mounting_plate.linear_extrude(self.dz)

    def build(self):
        return self.generate_key_row().translate([self.x, self.y, self.z])


class ArcBuilder(ModelBuilder):
    def __init__(self, width: float, len_height: float) -> None:
        super().__init__(0, 0, 0, width, len_height, len_height)

    def copy_and_modify(
        self,
        new_dx: OptionalCopyField = None,
        new_dyz: OptionalCopyField = None,
        new_x: OptionalCopyField = None,
        new_y: OptionalCopyField = None,
        new_z: OptionalCopyField = None,
    ):
        copy = ArcBuilder(
            resolve_optional_copy_field(self.dx, new_dx),
            resolve_optional_copy_field(self.dy, new_dyz),
        )
        copy.move(
            [
                resolve_optional_copy_field(self.x, new_x),
                resolve_optional_copy_field(self.y, new_y),
                resolve_optional_copy_field(self.z, new_z),
            ]
        )
        return copy

    def _arc(self):
        return (
            (cube([self.dy, self.dy, self.dx]) - cylinder(r=self.dz, h=self.dx))
            .rotateY(90)
            .translateZ(self.dz)
        )

    def build(self):
        return self._arc().translate([self.x, self.y, self.z])


def generate_backplate(white_keys: int, conf: ConfigSchema):
    wk_total_width = conf.white_key_dims.width_to_mm(conf)
    white_plate_len = conf.white_key_dims.length_to_mm(conf)
    total_len = white_plate_len + conf.dist_u + conf.mount_plate_width
    backplate = cube(
        [white_keys * wk_total_width, total_len, conf.backplate_dims.width_mm]
    )
    hole = cylinder(h=99999, r=conf.backplate_dims.screw_r_mm)
    if white_keys > 1:
        backplate -= hole.translate(
            [
                wk_total_width,
                white_plate_len - conf.stand_r_mm + conf.mount_plate_width,
                0,
            ]
        )
        backplate -= hole.translate(
            [
                wk_total_width * (white_keys - 1),
                white_plate_len - conf.stand_r_mm + conf.mount_plate_width,
                0,
            ]
        )
    return backplate
