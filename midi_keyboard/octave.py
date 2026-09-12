from typing import Any

from base_builders import GroupBuilder, RelativeCoords, XPos, YPos, ZPos
from common import (
    ArcBuilder,
    CubeBuilder,
    KeyRowBuilder,
    SlopeBuilder,
    SquareXPunchedSlopeBuilder,
    StandBuilder,
)
from configuration import ConfigSchema, KeyDimensions
from connectors import ConnectorBuilder
from constants import WHITE_TO_BLACK_KEY_RATIO, get_black_key_dist


class OctaveWhitePartBuilder(GroupBuilder):
    def __init__(self, white_keys: int, conf: ConfigSchema):
        assert white_keys <= 7
        self.white_keys = white_keys
        wk_total_width = conf.white_key_dims.width_to_mm(conf)
        octave_width = wk_total_width * white_keys
        distances = [conf.white_key_dims.key_offset_x(conf)] + [wk_total_width] * 7
        wk_len_offset = conf.white_key_dims.key_offset_y(conf)
        white_plate_len = conf.white_key_dims.length_to_mm(conf)

        # upper wall, with mx mounting holes
        self.key_row = KeyRowBuilder(
            octave_width, white_plate_len, distances, wk_len_offset, conf
        )
        self.male_connector = ConnectorBuilder(distances[0], white_plate_len, conf)
        self.female_connector = ConnectorBuilder(
            distances[0], white_plate_len, conf, male=False
        )
        self.front_wall = CubeBuilder(
            octave_width,
            conf.mount_plate_width,
            conf.base_height_mm + conf.mount_plate_width,
        )
        self.front_wall_slope = SlopeBuilder(
            octave_width - distances[0],
            wk_len_offset - conf.min_key_margin_mm,
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
            self.key_row,
            RelativeCoords(zpos=ZPos.BOTTOM),
            RelativeCoords(xpos=XPos.RIGHT, ypos=YPos.BACK),
        )
        self.left_stand.move_rel(self.key_row, RelativeCoords(zpos=ZPos.BOTTOM))
        self.right_stand.move_rel(self.key_row, RelativeCoords(zpos=ZPos.BOTTOM))

        self.left_stand.move([wk_total_width, white_plate_len - self.left_stand.r, 0])
        self.right_stand.move(
            [wk_total_width * (white_keys - 1), white_plate_len - self.right_stand.r, 0]
        )

        super().__init__(0, 0, 0, octave_width, white_plate_len, 0)
        self.update_size_and_loc()

    def build(self):
        model = (
            self.key_row.build()
            + self.male_connector.build()
            + self.female_connector.build()
            + self.front_wall.build()
            + self.front_wall_slope.build()
        )
        if self.white_keys > 1:
            model += self.left_stand.build() + self.right_stand.build()
        return model


class OctaveBlackPartBuilder(GroupBuilder):
    def __init__(self, white_keys: int, conf: ConfigSchema) -> None:
        assert white_keys <= 7

        wk_total_width = conf.white_key_dims.width_to_mm(conf)
        octave_width = wk_total_width * white_keys
        distances = get_black_key_dist(wk_total_width, conf.mount_u)

        bw_diff = conf.white_black_keys_offset_mm + conf.mount_plate_width

        self.key_row = KeyRowBuilder(
            octave_width,
            conf.dist_u,
            distances[: WHITE_TO_BLACK_KEY_RATIO[white_keys]],
            KeyDimensions(1, 1).key_offset_y(conf),
            conf,
        )
        self.middle_wall = CubeBuilder(octave_width, conf.mount_plate_width, bw_diff)
        self.outer_arc = ArcBuilder(octave_width, bw_diff)
        self.back_wall = CubeBuilder(
            octave_width, conf.mount_plate_width, bw_diff + conf.base_height_mm
        )
        self.male_connector = ConnectorBuilder(distances[0], conf.dist_u, conf)
        self.female_connector = ConnectorBuilder(
            distances[0], conf.dist_u, conf, male=False
        )
        self.internal_slope = SquareXPunchedSlopeBuilder(
            octave_width - self.female_connector.dx,
            conf.dist_u - conf.mount_plate_width,
            bw_diff,
            distances,
            (conf.mount_u, conf.dist_u),
        )
        self.back_wall.move_rel(
            self.key_row, RelativeCoords(ypos=YPos.BACK), RelativeCoords(zpos=ZPos.TOP)
        )
        self.middle_wall.move_rel(self.key_row, RelativeCoords(zpos=ZPos.BOTTOM))
        self.outer_arc.move_rel(
            self.middle_wall,
            RelativeCoords(ypos=YPos.FRONT),
            RelativeCoords(zpos=ZPos.BOTTOM),
        )
        self.female_connector.move_rel(self.key_row, RelativeCoords(zpos=ZPos.BOTTOM))
        self.male_connector.move_rel(
            self.key_row,
            RelativeCoords(zpos=ZPos.BOTTOM),
            RelativeCoords(xpos=XPos.RIGHT),
        )
        self.internal_slope.move_rel(
            self.female_connector,
            RelativeCoords(XPos.RIGHT),
            RelativeCoords(zpos=ZPos.TOP, ypos=YPos.BACK),
        )
        super().__init__(0, 0, 0, 0, 0, 0)
        self.update_size_and_loc()

    def build(self) -> Any:
        first, *rest = self.movable_parts
        model = first.build()
        for part in rest:
            model += part.build()
        return model.translate([self.x, self.y, self.z])


class OctaveBuilder(GroupBuilder):
    def __init__(self, white_keys: int, conf: ConfigSchema) -> None:
        self.black_part = OctaveBlackPartBuilder(white_keys, conf)
        self.white_part = OctaveWhitePartBuilder(white_keys, conf)

        self.white_part.move_rel(
            self.black_part.middle_wall,
            RelativeCoords(zpos=ZPos.TOP),
            RelativeCoords(ypos=YPos.FRONT),
        )

    def build(self) -> Any:
        return self.black_part.build() + self.white_part.build()


# def generate_octave(white_keys: int, conf: ConfigSchema):

#     assert bw_diff <= (conf.white_key_dims.key_offset_y(conf) - 1), (
#         "Distance between white and black keys is too high, cannot generate arc between them"
#     )

#     white_part, wp_male_connector_width, wp_male_connector_height = (
#         generate_kb_white_key_part(octave_width, white_keys, conf)
#     )

#     b_distances = get_black_key_dist(wk_total_width, conf.mount_u)
#     black_mount_plate = (
#         # middle wall, between black and white keys
#         +cube([octave_width, conf.mount_plate_width, bw_diff]).down(bw_diff)
#         # middle wall outer arc, to make connection between white and black keys part stronger
#         + arc(bw_diff, octave_width).up(conf.mount_plate_width)
#         # Back wall of the keyboard
#         + cube([octave_width, conf.mount_plate_width, bw_diff + conf.base_height_mm])
#         .down(bw_diff + conf.base_height_mm)
#         .translateY(conf.dist_u - conf.mount_plate_width)
#         + generate_female_connector(b_distances[0], conf.dist_u, conf)
#         + generate_male_connector(b_distances[0], conf.dist_u, conf).translateX(
#             octave_width
#         )
#         # slope between black and white part of the keyboard connector
#         + slope(
#             wp_male_connector_width, conf.dist_u, bw_diff + wp_male_connector_height
#         ).translate(
#             [
#                 octave_width - wp_male_connector_width,
#                 0,
#                 -(bw_diff + wp_male_connector_height),
#             ]
#         )
#     )
#     conn_width, _ = normalize_width_len_connector(b_distances[0], conf.dist_u)
#     mid_wall_inner_slope = slope(
#         octave_width - conn_width, bw_diff, bw_diff
#     ).translateX(conn_width)
#     key_hole = square([conf.mount_u, bw_diff]).linear_extrude(bw_diff)
#     for dist in accumulate(b_distances):
#         mid_wall_inner_slope -= key_hole.translateX(dist)

#     return (
#         black_mount_plate
#         + mid_wall_inner_slope.translateY(conf.mount_plate_width).down(bw_diff)
#         + white_part
#     )
