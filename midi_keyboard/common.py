from solid2 import square, circle, polygon
from solid2.extensions.bosl2 import round_corners

from configuration import ConfigSchema, KeyDimensions


def generate_keys_row(
    n: int, 
    key_dims: KeyDimensions,
    conf: ConfigSchema,
    plate_width: float,
    plate_length: float,
    initial_offest: float | None = None,
):
    key_width = key_dims.width * conf.dist_u
    key_len = key_dims.length * conf.dist_u
    u = conf.mount_u
    mx_hole = square([u, u], center=True).translateX(key_len / 2).translateY(key_width / 2)
    w_mounting_plate = square([plate_width, plate_length], center=True) - mx_hole
    w_mounting_plate_3d = w_mounting_plate.linear_extrude(conf.mount_plate_width)

    for _ in range(n):
        w_mounting_plate_3d -= mx_hole.translateY(key_width)

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
