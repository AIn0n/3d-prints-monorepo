from solid2 import cube

from connectors import generate_male_connector, generate_female_connector
from constants import get_black_key_dist

from configuration import ConfigSchema
from common import generate_keys_row, generate_slope, generate_stand


def generate_kb_white_key_part(
    wk_total_width: float, octave_width: float, white_keys: float, conf: ConfigSchema
):
    white_plate_len = conf.white_key_dims.length * conf.dist_u
    wk_len_offset = (white_plate_len - conf.mount_u) / 2
    w_distances = [(wk_total_width - conf.mount_u) / 2] + [wk_total_width] * 7
    plate = (
        # upper wall, with mx mounting holes
        generate_keys_row(
            octave_width,
            white_plate_len,
            w_distances[:white_keys],
            wk_len_offset,
            conf,
        )
        +
        # front wall of the keyboard
        cube([octave_width, conf.mount_plate_width, conf.base_height_mm]).down(
            conf.base_height_mm
        )
        # slope added to the first wall - probably better to remove supports
        + generate_slope(
            octave_width - w_distances[0],
            wk_len_offset
            - conf.mount_plate_width
            - 1,  # minimal offset from mounting point to fit switch
            conf.base_height_mm,
        )
        .translateX(w_distances[0])
        .translateY(conf.mount_plate_width)
        .down(conf.base_height_mm)
        # connectors
        + generate_female_connector(w_distances[0], white_plate_len, conf)
        + generate_male_connector(w_distances[0], white_plate_len, conf).translateX(
            octave_width
        )
    )
    if white_keys > 1:
        plate += generate_stand(wk_total_width, white_plate_len, conf)
        plate += generate_stand(
            wk_total_width * (white_keys - 1), white_plate_len, conf
        )
    return plate.translate(
        [
            0,
            -white_plate_len,
            -conf.white_black_keys_offset_mm - conf.mount_plate_width,
        ]
    )


def generate_octave(white_keys: int, conf: ConfigSchema):
    assert white_keys <= 7

    wk_total_width = conf.white_key_dims.width * conf.dist_u
    octave_width = wk_total_width * white_keys

    bw_diff = conf.white_black_keys_offset_mm + conf.mount_plate_width

    b_distances = get_black_key_dist(white_keys, wk_total_width, conf.mount_u)
    black_mount_plate = (
        generate_keys_row(
            octave_width,
            conf.dist_u,
            b_distances,
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
    return black_mount_plate + generate_kb_white_key_part(
        wk_total_width, octave_width, white_keys, conf
    )
