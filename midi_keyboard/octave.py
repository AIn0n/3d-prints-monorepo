from solid2 import cube, square

from connectors import ConnectorBuilder
from constants import get_black_key_dist, WHITE_TO_BLACK_KEY_RATIO
from itertools import accumulate
from functools import cached_property
from typing import Collection

from configuration import ConfigSchema
from common import (
    arc,
    KeyRowBuilder,
    CubeBuilder,
    SlopeBuilder,
    StandBuilder,
)
from model_builder import ModelBuilder, RelativeCoords, ZPos, XPos, YPos


class OctaveWhitePartBuilder(ModelBuilder):
    @cached_property
    def movable_parts(self) -> Collection[ModelBuilder]:
        return [attr for attr in vars(self).values if isinstance(attr, ModelBuilder)]

    def __init__(self, white_keys: int, conf: ConfigSchema):
        self.conf = conf
        self.white_keys = white_keys
        wk_total_width = conf.white_key_dims.width_to_mm(conf)
        octave_width = wk_total_width * white_keys
        w_distances = [conf.white_key_dims.key_offset_x(conf)] + [wk_total_width] * 7
        wk_len_offset = conf.white_key_dims.key_offset_y(conf)
        white_plate_len = conf.white_key_dims.length_to_mm(conf)

        # upper wall, with mx mounting holes
        self.key_row = KeyRowBuilder(
            octave_width, white_plate_len, w_distances, wk_len_offset, conf
        )
        self.male_connector = ConnectorBuilder(w_distances[0], white_plate_len, conf)
        self.female_connector = ConnectorBuilder(w_distances[0], white_plate_len, conf)
        self.front_wall = CubeBuilder(
            octave_width,
            conf.mount_plate_width,
            conf.base_height_mm + conf.mount_plate_width,
        )
        self.front_wall_slope = SlopeBuilder(
            octave_width - w_distances[0],
            wk_len_offset - conf.mount_plate_width - conf.min_key_margin_mm,
            conf.base_height_mm,
        )
        self.left_stand = StandBuilder(conf)
        self.right_stand = StandBuilder(conf)

        self.male_connector.move_rel(
            self.key_row,
            RelativeCoords(zpos=ZPos.BOTTOM),
            RelativeCoords(xpos=XPos.RIGHT, ypos=YPos.CENTER),
        )
        self.female_connector.move_rel(
            self.key_row,
            RelativeCoords(zpos=ZPos.BOTTOM),
            RelativeCoords(xpos=XPos.LEFT, ypos=YPos.CENTER),
        )
        self.front_wall.move_rel(
            self.key_row, RelativeCoords(ypos=YPos.FRONT), RelativeCoords(zpos=ZPos.TOP)
        )
        self.front_wall_slope.move_rel(
            self.front_wall,
            RelativeCoords(ypos=YPos.BACK),
            RelativeCoords(xpos=XPos.RIGHT, zpos=ZPos.BOTTOM),
        )
        self.left_stand.move_rel(self.key_row, RelativeCoords(zpos=ZPos.BOTTOM))
        self.right_stand.move_rel(self.key_row, RelativeCoords(zpos=ZPos.BOTTOM))

        self.left_stand.move([wk_total_width, white_plate_len - self.left_stand.r, 0])
        self.right_stand.move(
            [wk_total_width * (white_keys - 1), white_plate_len - self.right_stand.r, 0]
        )

        super().__init__(0, 0, 0, octave_width, white_plate_len, 0)

    def move_rel(
        self,
        other: ModelBuilder,
        anchor: RelativeCoords,
        alignment: RelativeCoords | None = None,
    ) -> None:
        for part in self.movable_parts:
            part.move_rel(other, anchor, alignment)

        return super().move_rel(other, anchor, alignment)

    def move(self, pos: tuple[float, float, float]) -> None:
        for part in self.movable_parts:
            part.move(pos)

        return super().move(pos)

    def build(self):
        model = (
            self.key_row.build()
            + self.male_connector.build(male=True)
            + self.female_connector.build(male=False)
            + self.front_wall.build()
            + self.front_wall_slope.build()
        )
        if self.white_keys > 1:
            model += self.left_stand.build() + self.right_stand.build()
        return model


def generate_octave(white_keys: int, conf: ConfigSchema):
    assert white_keys <= 7

    wk_total_width = conf.white_key_dims.width_to_mm(conf)
    octave_width = wk_total_width * white_keys

    bw_diff = conf.white_black_keys_offset_mm + conf.mount_plate_width

    assert bw_diff <= (conf.white_key_dims.key_offset_y(conf) - 1), (
        "Distance between white and black keys is too high, cannot generate arc between them"
    )

    white_part, wp_male_connector_width, wp_male_connector_height = (
        generate_kb_white_key_part(octave_width, white_keys, conf)
    )

    b_distances = get_black_key_dist(wk_total_width, conf.mount_u)
    black_mount_plate = (
        generate_keys_row(
            octave_width,
            conf.dist_u,
            b_distances[: WHITE_TO_BLACK_KEY_RATIO[white_keys]],
            (conf.dist_u - conf.mount_u) / 2,
            conf,
        )
        # middle wall, between black and white keys
        + cube([octave_width, conf.mount_plate_width, bw_diff]).down(bw_diff)
        # middle wall outer arc, to make connection between white and black keys part stronger
        + arc(bw_diff, octave_width).up(conf.mount_plate_width)
        # Back wall of the keyboard
        + cube([octave_width, conf.mount_plate_width, bw_diff + conf.base_height_mm])
        .down(bw_diff + conf.base_height_mm)
        .translateY(conf.dist_u - conf.mount_plate_width)
        + generate_female_connector(b_distances[0], conf.dist_u, conf)
        + generate_male_connector(b_distances[0], conf.dist_u, conf).translateX(
            octave_width
        )
        # slope between black and white part of the keyboard connector
        + slope(
            wp_male_connector_width, conf.dist_u, bw_diff + wp_male_connector_height
        ).translate(
            [
                octave_width - wp_male_connector_width,
                0,
                -(bw_diff + wp_male_connector_height),
            ]
        )
    )
    conn_width, _ = normalize_width_len_connector(b_distances[0], conf.dist_u)
    mid_wall_inner_slope = slope(
        octave_width - conn_width, bw_diff, bw_diff
    ).translateX(conn_width)
    key_hole = square([conf.mount_u, bw_diff]).linear_extrude(bw_diff)
    for dist in accumulate(b_distances):
        mid_wall_inner_slope -= key_hole.translateX(dist)

    return (
        black_mount_plate
        + mid_wall_inner_slope.translateY(conf.mount_plate_width).down(bw_diff)
        + white_part
    )
