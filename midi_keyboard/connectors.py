from common import floor_to_half
from base_builders import ModelBuilder
from configuration import ConfigSchema

from solid2 import square
from solid2.extensions.bosl2 import trapezoid


class ConnectorBuilder(ModelBuilder):
    def __init__(
        self,
        width: float,
        len_: float,
        conf: ConfigSchema,
        male: bool = True,
    ) -> None:
        self.conf = conf
        self.male = male
        x, y, z = [0, 0, 0]
        width, len_ = self._normalize_width_len_connector(width, len_)
        super().__init__(x, y, z, width, len_, self._compute_conn_height(width, conf))

    @staticmethod
    def _normalize_width_len_connector(
        width: float, len_: float
    ) -> tuple[float, float]:
        width, len_ = (width, len_) if len_ >= width * 2 else (len_ // 2, len_)
        return floor_to_half(width), len_

    @staticmethod
    def _compute_conn_height(width: float, conf: ConfigSchema) -> float:
        """Takes already normalized width"""
        return min(width, conf.base_height_mm)

    def generate_female_connector(self):
        w2 = self.dx + self.conf.connector_dims.base_diff_mm

        female_conn = (
            trapezoid(
                h=self.dx,
                w1=self.dx,
                w2=w2,
            )
            .linear_extrude(self.dz)
            .rotateZ(-90)
            .translateX(self.dx * 0.5)
        )
        conn = square([self.dx, self.dy]).linear_extrude(self.dz)

        offset = self.dx * 2
        conn_n = int(self.dy // offset)
        adjusted_offset = self.dy / conn_n

        for i in range(conn_n):
            conn -= female_conn.translateY(adjusted_offset / 2 + i * adjusted_offset)

        return conn

    def _generate_male_connector(self):
        margin = self.conf.connector_dims.margin_mm
        w2 = self.dx + self.conf.connector_dims.base_diff_mm - margin

        male_conn = (
            trapezoid(
                h=self.dx,
                w1=self.dx - margin,
                w2=w2,
            )
            .linear_extrude(self.dz - margin)
            .rotateZ(-90)
            .translateX(self.dx * 1.5)
        )
        conn = square([self.dx, self.dy]).linear_extrude(self.dz)

        offset = self.dx * 2
        conn_n = int(self.dy // offset)
        adjusted_offset = self.dy / conn_n

        for i in range(conn_n):
            conn += male_conn.translateY(adjusted_offset / 2 + i * adjusted_offset)

        return conn

    def build(self):
        model = (
            self._generate_male_connector()
            if self.male
            else self.generate_female_connector()
        )
        return model.translate([self.x, self.y, self.z])
