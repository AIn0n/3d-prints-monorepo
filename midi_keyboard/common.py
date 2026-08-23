from solid2 import square, cylinder, cube
from itertools import accumulate
from math import sqrt, atan2, degrees

from configuration import ConfigSchema


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
