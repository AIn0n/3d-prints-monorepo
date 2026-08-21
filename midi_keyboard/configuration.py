from dataclasses import dataclass, field
from omegaconf import OmegaConf
from pathlib import Path


@dataclass
class KeyDimensions:
    length: float
    width: float


@dataclass
class ConnectorDimensions:
    base_diff_mm: float = 2
    margin_mm: float = 0.06


@dataclass
class ConfigSchema:
    dist_u: float = 19.5
    white_key_dims: KeyDimensions = field(
        default_factory=lambda: KeyDimensions(length=1.75, width=1.25)
    )
    black_key_dims: KeyDimensions = field(
        default_factory=lambda: KeyDimensions(length=1.75, width=1.0)
    )

    rows_height_diff_mm: float = 12.0

    mount_plate_width: float = 1.25
    mount_u: float = 14

    keycap_u: float = 18
    keycap_height_mm: float = 1.0
    keycap_rounding_corner_mm: float = 2.0

    output_dir: Path = Path("./build/")

    white_black_keys_offset_mm: float = 6.0
    base_height_mm: float = 8.0
    connector_dims: ConnectorDimensions = field(default_factory=ConnectorDimensions)

    stand_r_mm: float = 5.0
    stand_screw_r_mm: float = 0.5


def load_config(path: Path = Path("default.conf.yaml")) -> OmegaConf:
    yaml_config = OmegaConf.load(path)

    schema = OmegaConf.structured(ConfigSchema)
    return OmegaConf.merge(schema, yaml_config)
