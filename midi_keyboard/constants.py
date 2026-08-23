WHITE_TO_BLACK_KEY_RATIO = {
    1: 0,
    2: 1,
    3: 2,
    4: 2,
    5: 3,
    6: 4,
    7: 5,
}


def get_black_key_dist(white_key_width: float, mount_width: float) -> list[float]:
    return [
        white_key_width - mount_width / 2,
        white_key_width,
        white_key_width * 2,
        white_key_width,
        white_key_width,
    ]
