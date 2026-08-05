from dataclasses import dataclass
from omegaconf import OmegaConf
from pathlib import Path

@dataclass
class ConfigSchema:
    u_dist: float = 19.5
    white_key_len: float = 1.75
    white_key_width: float = 1.25
    mount_plate_width: float = 1.25
    mount_u: float = 14

    keycap_u: float = 18
    keycap_height_mm: float = 1.0
    keycap_rounding_corner_mm: float = 2.0

    output_dir: Path = Path("./build/")

schema = OmegaConf.structured(ConfigSchema)