from base_builders import GroupBuilder, RelativeCoords, XPos, YPos, ZPos
from common import CubeBuilder
from configuration import ConfigSchema, KeyDimensions
from octave import OctaveBuilder


class CrontrollerCaseBuilder(GroupBuilder):
    def compute_total_dx(self, conf: ConfigSchema) -> float:
        """
        total width of the module is sum of: width of one key, width of the controller
        and width of the bigger connector
        """
        return conf.controller_width_mm + conf.dist_u + self.black_part_connector.dx

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
        key = KeyDimensions(1, 1)
        self.octave_up_key_hole = CubeBuilder(
            key.width_to_mm(conf), key.length_to_mm(conf), conf.mount_plate_width
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
        self.octave_up_key_hole.move(
            [-key.key_offset_x(conf), -key.key_offset_y(conf), 0]
        )
        self.octave_down_key_hole = self.octave_up_key_hole.copy_and_modify(
            new_y=lambda x: x - key.key_offset_y(conf) - key.length_to_mm(conf)
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
            - self.octave_up_key_hole.build()
            - self.octave_down_key_hole.build()
        )
