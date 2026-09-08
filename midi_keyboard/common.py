from solid2 import square, cylinder, cube
from itertools import accumulate
from math import sqrt, atan2, degrees, floor

from configuration import ConfigSchema
from model_builder import ModelBuilder


def floor_to_half(x):
    return floor(x * 2) / 2


def generate_stand(x: float, y: float, conf: ConfigSchema):
    return (
        cylinder(h=conf.base_height_mm, r=conf.stand_r_mm)
        - cylinder(h=conf.base_height_mm, r=conf.stand_screw_r_mm)
    ).translate(
        [
            x,
            y - conf.stand_r_mm,
            -conf.base_height_mm,
        ]
    )


class StandBuilder(ModelBuilder):
    def __init__(self, conf: ConfigSchema):
        diameter = conf.stand_r_mm * 2
        self.r = conf.stand_r_mm
        self.h = conf.base_height_mm
        self.hole_r = conf.stand_screw_r_mm
        super().__init__(0, 0, 0, diameter, diameter, conf.base_height_mm)

    def _slope(self):
        return cylinder(h=self.h, r=self.r) - cylinder(h=self.h, r=self.hole_r)

    def build(self):
        return self._slope().translate([self.x, self.y, self.z])


class SlopeBuilder(ModelBuilder):
    def __init__(self, dx, dy, dz):
        super().__init__(0, 0, 0, dx, dy, dz)

    def _slope(self):
        sqr = square([self.dx, self.dy])
        rad_angle = atan2(self.dy, self.dz)
        angle = degrees(rad_angle)

        return sqr.linear_extrude(self.dz) - sqr.linear_extrude(
            sqrt(self.dx**2 + self.dy**2)
        ).rotateX(-angle)

    def build(self):
        return self._slope().translate([self.x, self.y, self.z])


class CubeBuilder(ModelBuilder):
    def __init__(self, dx, dy, dz) -> None:
        super().__init__(0, 0, 0, dx, dy, dz)

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


def arc(len_height: float, width: float):
    return (
        (cube([len_height, len_height, width]) - cylinder(r=len_height, h=width))
        .rotateY(90)
        .translateY(-len_height)
    )


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
