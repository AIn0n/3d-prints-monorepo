from solid2 import square, circle, polygon, cube
from solid2.extensions.bosl2 import round_corners
from itertools import accumulate

from configuration import ConfigSchema
from connectors import generate_male_connector, generate_female_connector


def generate_octave(white_keys: int, conf: ConfigSchema):
    assert white_keys <= 7
    white_keys_to_black_num_mapping = {
        1: 0,
        2: 1,
        3: 2,
        4: 2,
        5: 3,
        6: 4,
        7: 5,
    }

    wk_total_width = conf.white_key_dims.width * conf.dist_u
    octave_width = wk_total_width * white_keys
    white_plate_len = conf.white_key_dims.length * conf.dist_u
    w_distances = [(wk_total_width - conf.mount_u) / 2] + [wk_total_width] * 7
    white_mount_plate = (
        generate_keys_row(
            octave_width,
            white_plate_len,
            w_distances[:white_keys],
            (white_plate_len - conf.mount_u) / 2,
            conf,
        )
        + cube([octave_width, conf.mount_plate_width, conf.base_height_mm]).down(
            conf.base_height_mm
        )
        + generate_female_connector(w_distances[0], white_plate_len, conf)
        + generate_male_connector(w_distances[0], white_plate_len, conf).translateX(
            octave_width
        )
    )

    bw_diff = conf.white_black_keys_offset_mm + conf.mount_plate_width
    b_distances = [
        wk_total_width - conf.mount_u / 2,
        wk_total_width,
        wk_total_width * 2,
        wk_total_width,
        wk_total_width,
    ]
    black_mount_plate = (
        generate_keys_row(
            octave_width,
            conf.dist_u,
            b_distances[: white_keys_to_black_num_mapping[white_keys]],
            (conf.dist_u - conf.mount_u) / 2,
            conf,
        )
        + cube([octave_width, conf.mount_plate_width, bw_diff]).down(bw_diff)
        + cube([octave_width, conf.mount_plate_width, bw_diff + conf.base_height_mm])
        .down(bw_diff + conf.base_height_mm)
        .translateY(conf.dist_u - conf.mount_plate_width)
        + generate_female_connector(b_distances[0], conf.dist_u, conf)
        + generate_male_connector(b_distances[0], conf.dist_u, conf).translateX(
            octave_width
        )
    )

    return black_mount_plate + white_mount_plate.translate(
        [
            0,
            -white_plate_len,
            -conf.white_black_keys_offset_mm - conf.mount_plate_width,
        ]
    )


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
