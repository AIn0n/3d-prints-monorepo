from base_builders import *
from configuration import ConfigSchema
from common import CubeBuilder, StandBuilder
from solid2 import cylinder


def flatten_groups(group: GroupBuilder) -> list[ModelBuilder]:
    res = []
    for el in group.movable_parts:
        if isinstance(el, GroupBuilder):
            res.extend(flatten_groups(el))
        else:
            res.append(el)
    return res


class BackplateBuilder(GroupBuilder):
    def __init__(self, model: GroupBuilder, conf: ConfigSchema) -> None:
        self.c = CubeBuilder(model.dx, model.dy, conf.backplate_dims.width_mm)
        self.c.move_rel(
            model,
            RelativeCoords(zpos=ZPos.BOTTOM),
            RelativeCoords(ypos=YPos.FRONT, xpos=XPos.LEFT),
        )
        self.stands_cords = [
            (el.x, el.y) for el in flatten_groups(model) if isinstance(el, StandBuilder)
        ]
        self.hole_r = conf.backplate_dims.screw_r_mm
        super().__init__()

    def build(self):
        model = self.c.build()
        for x, y in self.stands_cords:
            model -= cylinder(h=self.dz, r=self.hole_r).translate([x, y, self.z])
        return model
