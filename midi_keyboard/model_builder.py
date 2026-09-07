from dataclasses import dataclass, asdict

from enum import Enum, auto


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


class ModelBuilder:
    def __init__(self, x: float, y: float, z: float, dx: float, dy: float, dz: float):

        self.x: float = x
        self.y: float = y
        self.z: float = z
        self.dx: float = dx
        self.dy: float = dy
        self.dz: float = dz

    def move(self, pos: tuple[float, float, float]) -> None:
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
                self.x -= self.dx
            else:
                self.x += other.dx

        if anchor.ypos is not None:
            if anchor.ypos == YPos.FRONT:
                self.y -= self.dy
            else:
                self.y += other.dy

        if anchor.zpos is not None:
            if anchor.zpos == ZPos.BOTTOM:
                self.z -= self.dz
            else:
                self.z += other.dz

        if alignment is None:
            return None

        if alignment.xpos is not None:
            if alignment.xpos == XPos.LEFT:
                self.x = other.x
            elif alignment.xpos == XPos.CENTER:
                self.x = (self.dx - other.dx) / 2
            else:
                self.x = self.dx - other.dx

        if alignment.ypos is not None:
            if alignment.ypos == YPos.FRONT:
                self.y = other.y
            elif alignment.ypos == YPos.CENTER:
                self.y = (self.dy - other.dy) / 2
            else:
                self.y = self.dy - other.dy

        if alignment.zpos is not None:
            if alignment.zpos == ZPos.TOP:
                self.z = other.z
            elif alignment.zpos == YPos.CENTER:
                self.z = (self.dz - other.dz) / 2
            else:
                self.z = self.dz - other.dz
