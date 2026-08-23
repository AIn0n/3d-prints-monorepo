from configuration import load_config
from mx_keys import generate_key
from octave import generate_octave
from constants import WHITE_TO_BLACK_KEY_RATIO


def generate_all():
    conf = load_config()
    conf.output_dir.mkdir(parents=True, exist_ok=True)

    full_octaves = conf.midi_keys_count // 12
    black_keys_cnt = full_octaves * 5
    white_keys_cnt = full_octaves * 7

    octave_path = conf.output_dir / "full_octave.stl"
    generate_octave(7, conf).save_as_stl(octave_path)
    print(f"Generated full octave model at {octave_path}")
    print(f"Print it {full_octaves} times\n")

    free_keys = conf.midi_keys_count % 12
    assert free_keys >= 0

    if free_keys > 0:
        partial_octave_keys = max(
            filter(lambda x: sum(x) <= free_keys, WHITE_TO_BLACK_KEY_RATIO.items()),
            key=sum,
        )
        partial_octave_wk_cnt, partial_octave_bk_cnt = partial_octave_keys

        partial_octave_path = conf.output_dir / "octave_small_ah.stl"
        generate_octave(partial_octave_wk_cnt, conf).save_as_stl()
        print(
            f"Generated partial octave at {partial_octave_path}\n"
            f"Number of playable keys: {partial_octave_wk_cnt + partial_octave_bk_cnt}\n"
            "Print it only once\n"
        )

        black_keys_cnt += partial_octave_bk_cnt
        white_keys_cnt += partial_octave_wk_cnt

    black_key_path = conf.output_dir / "black_keycap.stl"
    generate_key(
        conf.black_key_dims.width, conf.black_key_dims.length, conf
    ).save_as_stl(black_key_path)
    print(f"Generated black key stl at {black_key_path}")
    print(f"Print it {black_keys_cnt} times\n")

    white_key_path = conf.output_dir / "white_keycap.stl"
    generate_key(
        conf.white_key_dims.width, conf.white_key_dims.length, conf
    ).save_as_stl(white_key_path)
    print(f"Generated white key stl at {white_key_path}")
    print(f"Print it {white_keys_cnt} times")


if __name__ == "__main__":
    generate_all()
