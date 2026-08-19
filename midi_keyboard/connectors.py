from configuration import ConfigSchema

from solid2 import square
from solid2.extensions.bosl2 import trapezoid


def normalize_width_len_connector(width: float, len_: float) -> tuple[float, float]:
    return (width, len_) if len_ >= width * 2 else (len_ // 2, len_)


def generate_female_connector(
    width: float, len_: float, conf: ConfigSchema, downscale: bool = True
):
    width, len_ = normalize_width_len_connector(width, len_)
    conn_height = min(width, conf.base_height_mm)
    w2 = width + conf.connector_dims.base_diff_mm

    female_conn = (
        trapezoid(
            h=width,
            w1=width,
            w2=w2,
        )
        .linear_extrude(conn_height)
        .rotateZ(-90)
        .translateX(width * 0.5)
    )
    conn = square([width, len_]).linear_extrude(conn_height)

    offset = width * 2
    conn_n = int(len_ // offset)
    adjusted_offset = len_ / conn_n

    for i in range(conn_n):
        conn -= female_conn.translateY(adjusted_offset / 2 + i * adjusted_offset)

    return conn.down(width) if downscale else conn


def generate_male_connector(width: float, len_: float, conf: ConfigSchema):
    margin = conf.connector_dims.margin_mm

    conn_height = min(width, conf.base_height_mm)
    w2 = width + conf.connector_dims.base_diff_mm - margin

    male_conn = (
        trapezoid(
            h=width,
            w1=width - margin,
            w2=w2,
        )
        .linear_extrude(conn_height - margin)
        .rotateZ(-90)
        .translateX(width * 1.5)
    )
    conn = square([width, len_]).linear_extrude(conn_height)

    offset = width * 2
    conn_n = int(len_ // offset)
    adjusted_offset = len_ / conn_n

    for i in range(conn_n):
        conn += male_conn.translateY(adjusted_offset / 2 + i * adjusted_offset)

    return conn
