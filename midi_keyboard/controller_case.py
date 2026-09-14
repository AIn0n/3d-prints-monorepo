from base_builders import GroupBuilder, RelativeCoords, XPos, YPos, ZPos
from common import CubeBuilder
from configuration import ConfigSchema
from octave import OctaveBuilder


class CrontrollerCaseBuilder(GroupBuilder):
    def __init__(self, octave: OctaveBuilder, conf: ConfigSchema):
        self.black_part_connector = octave.black_part.male_connector
        self.white_part_connector = octave.white_part.male_connector
        self.top_wall = CubeBuilder(
            conf.controller_case_widht_mm, octave.dy, conf.mount_plate_width
        )
        self.back_wall = octave.black_part.back_wall.copy_and_modify(
            new_dx=conf.controller_case_widht_mm
        )
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

        super().__init__()

    def build(self):
        return self.build_all()
