from abc import ABC, abstractmethod
from dataclasses import asdict, dataclass
from enum import Enum, auto
from functools import cached_property
from typing import Any, Collection, Sequence


class XPos(Enum):
    LEFT = auto()
    CENTER = auto()
    RIGHT = auto()


class YPos(Enum):
    FRONT = auto()
    CENTER = auto()
    BACK = auto()


class ZPos(Enum):
    TOP = auto()
    CENTER = auto()
    BOTTOM = auto()


@dataclass
class RelativeCoords:
    xpos: XPos | None = None
    ypos: YPos | None = None
    zpos: ZPos | None = None


class ModelBuilder(ABC):
    def __init__(self, x: float, y: float, z: float, dx: float, dy: float, dz: float):
        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.dx: float = dx
        self.dy: float = dy
        self.dz: float = dz

    def move(self, pos: Sequence[float]) -> None:
        assert len(pos) == 3
        self.x += pos[0]
        self.y += pos[1]
        self.z += pos[2]

    def move_rel(
        self,
        other: ModelBuilder,
        anchor: RelativeCoords,
        alignment: RelativeCoords | None = None,
    ) -> None:
        self.x = other.x
        self.y = other.y
        self.z = other.z

        assert any(asdict(anchor).values()), (
            "At least one value to anchor have to be set up"
        )

        if anchor.xpos is not None:
            if anchor.xpos == XPos.LEFT:
                self.x = other.x - self.dx
            else:
                self.x = other.x + other.dx

        if anchor.ypos is not None:
            if anchor.ypos == YPos.FRONT:
                self.y = other.y - self.dy
            else:
                self.y = other.y + other.dy

        if anchor.zpos is not None:
            if anchor.zpos == ZPos.BOTTOM:
                self.z = other.z - self.dz
            else:
                self.z = other.z + other.dz

        if alignment is None:
            return None

        if alignment.xpos is not None:
            self.x = other.x
            if alignment.xpos == XPos.CENTER:
                self.x += (other.dx - self.dx) / 2
            elif alignment.xpos == XPos.RIGHT:
                self.x += other.dx - self.dx

        if alignment.ypos is not None:
            self.y = other.y
            if alignment.ypos == YPos.CENTER:
                self.y += (other.dy - self.dy) / 2
            elif alignment.ypos == YPos.FRONT:
                self.y += other.dy - self.dy

        if alignment.zpos is not None:
            self.z = other.z
            if alignment.zpos == ZPos.CENTER:
                self.z += (other.dz - self.dz) / 2
            elif alignment.zpos == ZPos.TOP:
                self.z += other.dz - self.dz

    @abstractmethod
    def build(self) -> Any: ...


class GroupBuilder(ModelBuilder):
    @cached_property
    def movable_parts(self) -> Collection[ModelBuilder]:
        return [attr for attr in vars(self).values() if isinstance(attr, ModelBuilder)]

    def update_size_and_loc(self) -> None:
        self.x = min_x = min(el.x for el in self.movable_parts)
        self.y = min_y = min(el.y for el in self.movable_parts)
        self.z = min_z = min(el.z for el in self.movable_parts)

        max_x = max(el.x + el.dx for el in self.movable_parts)
        max_y = max(el.y + el.dy for el in self.movable_parts)
        max_z = max(el.z + el.dz for el in self.movable_parts)

        self.dx = max_x - min_x
        self.dy = max_y - min_y
        self.dz = max_z - min_z

    def move_rel(
        self,
        other: ModelBuilder,
        anchor: RelativeCoords,
        alignment: RelativeCoords | None = None,
    ) -> None:
        old_x, old_y, old_z = self.x, self.y, self.z
        super().move_rel(other, anchor, alignment)
        offset_x = self.x - old_x
        offset_y = self.y - old_y
        offset_z = self.z - old_z

        self.move([offset_x, offset_y, offset_z])

    def move(self, pos: Sequence[float]) -> None:
        for part in self.movable_parts:
            part.move(pos)

        return super().move(pos)
