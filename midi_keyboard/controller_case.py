from base_builders import GroupBuilder, RelativeCoords, XPos, YPos, ZPos
from common import (
    CubeBuilder,
    InvertedArcBuilder,
    SlopeBuilder,
    StandBuilder,
    XRoundedCubeBuilder,
)
from configuration import ConfigSchema, KeyDimensions
from octave import OctaveBuilder


class CrontrollerCaseBuilder(GroupBuilder):
    def compute_total_dx(self, conf: ConfigSchema) -> float:
        """
        total width of the module is sum of: width of one key, width of the controller
        and width of the bigger connector
        """
        return (
            conf.controller_width_mm
            + conf.dist_u
            + self.black_part_connector.dx
            + conf.mount_plate_width
            + KeyDimensions(1, 1).key_offset_x(conf)
        )

    def __init__(self, octave: OctaveBuilder, conf: ConfigSchema):
        self.black_part_connector = octave.black_part.male_connector
        self.white_part_connector = octave.white_part.male_connector
        total_dx = self.compute_total_dx(conf)
        self.top_wall = CubeBuilder(total_dx, octave.dy, conf.mount_plate_width)
        self.back_wall = octave.black_part.back_wall.copy_and_modify(new_dx=total_dx)
        self.front_wall = self.back_wall.copy_and_modify()
        self.left_wall = CubeBuilder(
            conf.mount_plate_width,
            self.top_wall.dy,
            self.back_wall.dz + conf.mount_plate_width,
        )
        self.white_connector_cover = CubeBuilder(
            self.white_part_connector.dx,
            self.white_part_connector.dy,
            self.top_wall.z - self.white_part_connector.end_z,
        )
        self.connector_slope = octave.male_connectors_slope.copy_and_modify()
        self.left_stand = StandBuilder(self.front_wall.dz, conf)
        self.right_stand = StandBuilder(self.front_wall.dz, conf)
        self.port_hole = XRoundedCubeBuilder(
            conf.mount_plate_width * 2,
            conf.controller_len_mm,
            conf.controller_height_mm,
        )
        self.front_arc = InvertedArcBuilder(
            total_dx + conf.mount_plate_width, conf.front_arc_r_mm
        )
        self.octave_up_key_hole = CubeBuilder(
            conf.mount_u, conf.mount_u, conf.mount_plate_width
        )

        self.back_wall.move_rel(
            self.black_part_connector,
            RelativeCoords(ypos=YPos.BACK),
            RelativeCoords(xpos=XPos.RIGHT, zpos=ZPos.TOP),
        )
        self.top_wall.move_rel(
            self.back_wall,
            RelativeCoords(zpos=ZPos.TOP),
            RelativeCoords(xpos=XPos.RIGHT, ypos=YPos.BACK),
        )
        self.front_wall.move_rel(
            self.top_wall,
            RelativeCoords(zpos=ZPos.BOTTOM),
            RelativeCoords(xpos=XPos.LEFT, ypos=YPos.FRONT),
        )
        self.left_wall.move_rel(
            self.top_wall,
            RelativeCoords(xpos=XPos.LEFT),
            RelativeCoords(ypos=YPos.CENTER, zpos=ZPos.TOP),
        )
        self.white_connector_cover.move_rel(
            self.black_part_connector,
            RelativeCoords(ypos=YPos.FRONT),
            RelativeCoords(xpos=XPos.RIGHT, zpos=ZPos.TOP),
        )
        self.connector_slope.move_rel(
            self.white_part_connector,
            RelativeCoords(ypos=YPos.BACK),
            RelativeCoords(xpos=XPos.CENTER, zpos=ZPos.BOTTOM),
        )

        self.octave_up_key_hole.move_rel(
            self.black_part_connector,
            RelativeCoords(xpos=XPos.LEFT, zpos=ZPos.TOP),
            RelativeCoords(ypos=YPos.BACK),
        )
        key = KeyDimensions(1, 1)
        self.octave_up_key_hole.move(
            [-key.key_offset_x(conf), -key.key_offset_y(conf), 0]
        )
        mount_keycap_diff = (conf.dist_u - conf.mount_u) / 2
        self.octave_down_key_hole = self.octave_up_key_hole.copy_and_modify(
            new_y=lambda x: x - (mount_keycap_diff + conf.mount_u)
        )

        assert conf.controller_len_mm < octave.dy
        self.controller_slope = SlopeBuilder(
            self.octave_up_key_hole.x - self.front_wall.x,
            self.back_wall.y - self.front_wall.end_y - conf.controller_len_mm,
            self.front_wall.dz,
        )
        self.black_connector_support = CubeBuilder(
            self.black_part_connector.dx,
            self.black_part_connector.y - self.front_wall.end_y,
            self.black_part_connector.dz,
        )
        self.black_connector_support.move_rel(
            self.black_part_connector,
            RelativeCoords(ypos=YPos.FRONT),
            RelativeCoords(xpos=XPos.CENTER, zpos=ZPos.BOTTOM),
        )

        self.key_slope = SlopeBuilder(
            self.front_wall.end_x - self.octave_up_key_hole.x,
            self.octave_down_key_hole.y
            - conf.min_key_margin_mm
            - self.front_wall.end_y,
            self.front_wall.dz,
        )

        self.key_slope.move_rel(
            self.front_wall,
            RelativeCoords(ypos=YPos.BACK),
            RelativeCoords(xpos=XPos.RIGHT, zpos=ZPos.BOTTOM),
        )

        self.controller_slope.move_rel(
            self.front_wall,
            RelativeCoords(ypos=YPos.BACK),
            RelativeCoords(xpos=XPos.LEFT, zpos=ZPos.BOTTOM),
        )
        self.left_stand.move_rel(
            self.controller_slope,
            RelativeCoords(ypos=YPos.BACK),
            RelativeCoords(xpos=XPos.LEFT, ypos=YPos.BACK, zpos=ZPos.TOP),
        )
        self.left_stand.move([self.left_stand.r, 0, 0])
        self.right_stand.move_rel(
            self.controller_slope,
            RelativeCoords(ypos=YPos.BACK),
            RelativeCoords(xpos=XPos.RIGHT, ypos=YPos.BACK, zpos=ZPos.TOP),
        )
        self.port_hole.move_rel(
            self.back_wall,
            RelativeCoords(xpos=XPos.LEFT, ypos=YPos.FRONT),
            RelativeCoords(zpos=ZPos.TOP),
        )
        self.front_arc.move_rel(
            self.left_wall,
            RelativeCoords(zpos=ZPos.TOP),
            RelativeCoords(xpos=XPos.LEFT, ypos=YPos.FRONT, zpos=ZPos.TOP),
        )

        super().__init__()

    def build(self):
        return (
            self.black_part_connector.build()
            + self.white_part_connector.build()
            + self.top_wall.build()
            + self.back_wall.build()
            + self.front_wall.build()
            + self.white_part_connector.build()
            + self.connector_slope.build()
            + self.white_connector_cover.build()
            + self.left_wall.build()
            + self.black_connector_support.build()
            + self.key_slope.build()
            + self.controller_slope.build()
            + self.left_stand.build()
            + self.right_stand.build()
            - self.port_hole.build()
            - self.octave_up_key_hole.build()
            - self.octave_down_key_hole.build()
            - self.front_arc.build()
        )
