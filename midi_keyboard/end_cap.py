from base_builders import GroupBuilder, RelativeCoords, XPos, YPos, ZPos
from common import CubeBuilder, SlopeBuilder, StandBuilder
from configuration import ConfigSchema
from octave import OctaveBuilder


class EndCapBuilder(GroupBuilder):
    def compute_dx(self, octave: OctaveBuilder, conf: ConfigSchema) -> float:
        return max(
            octave.black_part.female_connector.dx,
            octave.white_part.female_connector.dx + conf.stand_r_mm * 2,
        )

    def __init__(self, octave: OctaveBuilder, conf: ConfigSchema) -> None:
        self.black_part_connector = octave.black_part.female_connector
        self.white_part_connector = octave.white_part.female_connector
        total_dx_excl_wall = self.compute_dx(octave, conf)
        total_dx = total_dx_excl_wall + conf.mount_plate_width
        self.black_part_wall = octave.black_part.key_row.to_cube().copy_and_modify(
            new_dx=total_dx_excl_wall,
            new_x=0,
        )
        self.white_part_wall = octave.white_part.key_row.to_cube().copy_and_modify(
            new_dx=total_dx_excl_wall, new_x=0
        )
        self.mid_wall = octave.black_part.middle_wall.copy_and_modify(
            new_dx=total_dx, new_x=0
        )
        self.arc = octave.black_part.outer_arc.copy_and_modify(new_dx=total_dx, new_x=0)
        self.back_wall = octave.black_part.back_wall.copy_and_modify(
            new_dx=total_dx, new_x=0
        )
        self.front_wall = octave.white_part.front_wall.copy_and_modify(
            new_dx=total_dx,
            new_x=0,
        )
        stand_height = self.white_part_wall.z - self.front_wall.z
        self.back_stand = StandBuilder(stand_height, conf)
        self.front_stand = StandBuilder(stand_height, conf)
        self.black_cap = CubeBuilder(
            conf.mount_plate_width, self.black_part_connector.dy, self.back_wall.dz
        )
        self.white_cap = CubeBuilder(
            conf.mount_plate_width,
            self.white_part_connector.dy,
            self.front_wall.dz,
        )
        self.front_wall_support_slope = SlopeBuilder(
            total_dx_excl_wall - self.white_part_connector.dx,
            self.mid_wall.end_y - self.front_wall.end_y,
            self.front_wall.dz - conf.mount_plate_width,
        )

        self.black_cap.move_rel(
            self.black_part_wall,
            RelativeCoords(xpos=XPos.RIGHT),
            RelativeCoords(ypos=YPos.BACK, zpos=ZPos.TOP),
        )
        self.white_cap.move_rel(
            self.white_part_wall,
            RelativeCoords(xpos=XPos.RIGHT),
            RelativeCoords(ypos=YPos.BACK, zpos=ZPos.TOP),
        )
        self.front_wall_support_slope.move_rel(
            self.white_cap,
            RelativeCoords(xpos=XPos.LEFT),
            RelativeCoords(ypos=YPos.FRONT, zpos=ZPos.BOTTOM),
        )
        self.front_stand.move_rel(
            self.white_part_wall,
            RelativeCoords(zpos=ZPos.BOTTOM),
            RelativeCoords(xpos=XPos.RIGHT, ypos=YPos.FRONT),
        )
        self.front_stand.move([0, self.front_stand.r, 0])
        self.back_stand.move_rel(
            self.white_part_wall,
            RelativeCoords(zpos=ZPos.BOTTOM),
            RelativeCoords(xpos=XPos.RIGHT, ypos=YPos.BACK),
        )
        self.mid_wall_support = CubeBuilder(
            self.black_cap.x - self.black_part_connector.end_x,
            self.black_part_connector.dy,
            self.mid_wall.dz,
        )
        self.mid_wall_support.move_rel(
            self.black_part_connector,
            RelativeCoords(xpos=XPos.RIGHT),
            RelativeCoords(ypos=YPos.CENTER, zpos=ZPos.TOP),
        )
        super().__init__()

    def build(self):
        return self.build_all()
