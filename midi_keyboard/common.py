from solid2 import square, circle, polygon
from solid2.extensions.bosl2 import round_corners

from configuration import ConfigSchema, KeyDimensions


def generate_mx_stem():
    mx_stem_l = 4.0
    mx_stem_w = 1.2
    mx_stem_h = 3.0

    mx_stem_arm = square([mx_stem_l, mx_stem_w], center=True)
    mx_stem_base = circle(d=5.5) - (mx_stem_arm + mx_stem_arm.rotateZ(90))

    return mx_stem_base.linear_extrude(height=mx_stem_h)


def generate_key(width: float, length: float, conf: ConfigSchema):
    stem = generate_mx_stem()
    u = conf.keycap_u
    h = conf.keycap_height_mm

    keycap_base = square([u * width, u * length], center=True)
    rounded_keycap = polygon(
        round_corners(path=keycap_base, radius=conf.keycap_rounding_corner_mm)
    ).linear_extrude(height=h)
    return rounded_keycap + stem.up(h - 0.01)
