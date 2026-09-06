from solid2 import square, cylinder, cube
from itertools import accumulate
from math import sqrt, atan2, degrees, floor
from dataclasses import dataclass

from enum import Enum, auto

from configuration import ConfigSchema


def floor_to_half(x):
    return floor(x * 2) / 2


class Anchor(Enum):
    bottom_front_left = auto()
    bottom_front_right = auto()
    bottom_back_left = auto()
    bottom_back_right = auto()
    top_front_left = auto()
    top_front_right = auto()
    top_back_left = auto()
    top_back_right = auto()


class ModelBuilder:
    def __init__(self, x: float, y: float, z: float, dx: float, dy: float, dz: float):

        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.dx: float = dx
        self.dy: float = dy
        self.dz: float = dz

    def move(self, pos: tuple[float, float, float]) -> None:
        self.x += pos[0]
        self.y += pos[1]
        self.z += pos[2]

    def move_anchor(self, anchor: Anchor) -> None:
        match anchor:
            case Anchor.bottom_front_right:
                self.y -= self.dy
            case Anchor.bottom_back_left:
                self.x -= self.dx
            case Anchor.bottom_back_right:
                self.x -= self.dx
                self.y -= self.dy
            case Anchor.top_front_left:
                self.z -= self.dz
            case Anchor.top_front_right:
                self.z -= self.dz
                self.y -= self.dy
            case Anchor.top_back_left:
                self.z -= self.dz
                self.x -= self.dx
            case Anchor.top_back_right:
                self.z -= self.dz
                self.x -= self.dx
                self.y -= self.dy


def slope(width: float, len_: float, height: float):
    sqr = square([width, len_])
    rad_angle = atan2(len_, height)
    angle = degrees(rad_angle)

    return sqr.linear_extrude(height) - sqr.linear_extrude(
        sqrt(width**2 + len_**2)
    ).rotateX(-angle)


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


def generate_keys_row(
    plate_width: float,
    plate_length: float,
    key_sep_distances: list[float],
    y_offset: float,
    conf: ConfigSchema,
):
    u = conf.mount_u
    mx_hole = square([u, u]).translateY(y_offset)
    mounting_plate = square([plate_width, plate_length])

    for sep in accumulate(key_sep_distances):
        mounting_plate -= mx_hole.translateX(sep)

    return mounting_plate.linear_extrude(conf.mount_plate_width)


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
