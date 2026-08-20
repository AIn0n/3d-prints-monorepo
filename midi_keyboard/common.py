from solid2 import square, cube, cylinder
from itertools import accumulate

from configuration import ConfigSchema
from connectors import generate_male_connector, generate_female_connector
from constants import WHITE_TO_BLACK_KEY_RATIO


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


def generate_octave(white_keys: int, conf: ConfigSchema):
    assert white_keys <= 7

    wk_total_width = conf.white_key_dims.width * conf.dist_u
    octave_width = wk_total_width * white_keys
    white_plate_len = conf.white_key_dims.length * conf.dist_u
    w_distances = [(wk_total_width - conf.mount_u) / 2] + [wk_total_width] * 7
    white_mount_plate = (
        # upper wall, with mx mounting holes
        generate_keys_row(
            octave_width,
            white_plate_len,
            w_distances[:white_keys],
            (white_plate_len - conf.mount_u) / 2,
            conf,
        )
        # front wall of the keyboard
        + cube([octave_width, conf.mount_plate_width, conf.base_height_mm]).down(
            conf.base_height_mm
        )
        # connectors
        + generate_female_connector(w_distances[0], white_plate_len, conf)
        + generate_male_connector(w_distances[0], white_plate_len, conf).translateX(
            octave_width
        )
    )

    if white_keys > 1:
        white_mount_plate += generate_stand(wk_total_width, white_plate_len, conf)
        white_mount_plate += generate_stand(
            wk_total_width * (white_keys - 1), white_plate_len, conf
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
            b_distances[: WHITE_TO_BLACK_KEY_RATIO[white_keys]],
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
