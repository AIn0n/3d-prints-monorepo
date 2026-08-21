from configuration import load_config
from mx_keys import generate_key
from common import generate_octave


def generate_all():
    conf = load_config()
    conf.output_dir.mkdir(parents=True, exist_ok=True)

    generate_key(
        conf.black_key_dims.width, conf.black_key_dims.length, conf
    ).save_as_stl(conf.output_dir / "black_keycap.stl")

    generate_key(
        conf.white_key_dims.width, conf.white_key_dims.length, conf
    ).save_as_stl(conf.output_dir / "white_keycap.stl")

    generate_octave(2, conf).save_as_stl(conf.output_dir / "octave_small_ah.stl")
    generate_octave(7, conf).save_as_stl(conf.output_dir / "full_octave.stl")


if __name__ == "__main__":
    generate_all()
