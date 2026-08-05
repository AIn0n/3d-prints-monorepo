from solid2 import square, circle, polygon
from solid2.extensions.bosl2 import round_corners

from omegaconf import OmegaConf
from configuration import ConfigSchema


def generate_keys_row(n: int, conf: ConfigSchema):
    u = conf.mount_u
    white_key_len = conf.white_key_len
    white_key_dist = conf.u_dist * conf.white_key_width
    mx_hole = square([u, u], center=True)
    w_mounting_plate = square([white_key_len, white_key_dist], center=True) - mx_hole
    w_mounting_plate_3d = w_mounting_plate.linear_extrude(conf.mount_plate_width)

    for _ in range(n):
        w_mounting_plate_3d += w_mounting_plate_3d.translateY(white_key_dist)

    return w_mounting_plate_3d


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

    keycap_base = square([u * width, u * length], center= True)
    rounded_keycap = polygon(
        round_corners(path=keycap_base, radius=conf.keycap_rounding_corner_mm)
    ).linear_extrude(height=h)    
    return rounded_keycap + stem.up(h - 0.01)