from mjai.mlibriichi.tools import find_improving_tiles  # noqa, type: ignore


def convert_tehai_vec34_as_tenhou(
    tehai_vec34: list[int], akas_in_hand: list[bool] | None = None
) -> str:
    """
    Convert tehai_vec34 to tenhou.net/2 format

    TODO: support for called tiles
    """
    ms, ps, ss, zis = [], [], [], []
    shortline_elems = []
    for tile_idx, tile_count in enumerate(tehai_vec34):
        if tile_idx == 4:
            if akas_in_hand and akas_in_hand[0]:
                ms.append(0)
            ms += [5] * (
                tile_count - 1
                if akas_in_hand and akas_in_hand[0]
                else tile_count
            )
        elif tile_idx == 4 + 9:
            if akas_in_hand and akas_in_hand[1]:
                ps.append(0)
            ps += [5] * (
                tile_count - 1
                if akas_in_hand and akas_in_hand[1]
                else tile_count
            )
        elif tile_idx == 4 + 18:
            if akas_in_hand and akas_in_hand[2]:
                ps.append(0)
            ss += [5] * (
                tile_count - 1
                if akas_in_hand and akas_in_hand[2]
                else tile_count
            )
        elif tile_idx < 9:
            ms += [tile_idx + 1] * tile_count
        elif tile_idx < 18:
            ps += [tile_idx - 9 + 1] * tile_count
        elif tile_idx < 27:
            ss += [tile_idx - 18 + 1] * tile_count
        else:
            zis += [tile_idx - 27 + 1] * tile_count
    if len(ms) > 0:
        shortline_elems.append("".join(map(str, ms)) + "m")
    if len(ps) > 0:
        shortline_elems.append("".join(map(str, ps)) + "p")
    if len(ss) > 0:
        shortline_elems.append("".join(map(str, ss)) + "s")
    if len(zis) > 0:
        shortline_elems.append("".join(map(str, zis)) + "z")

    return "".join(shortline_elems)


def vec34_index_to_tenhou_tile(index: int) -> str:
    """
    Vec34 index to tenhou.net/2 format

    Example:
        >>> vec34_index_to_tenhou_tile(0)
        "1m"
        >>> vec34_index_to_tenhou_tile(33)
        "7z"
    """
    if index < 0 or index > 33:
        raise ValueError(f"index {index} is out of range [0, 33]")

    tiles = [
        "1m",
        "2m",
        "3m",
        "4m",
        "5m",
        "6m",
        "7m",
        "8m",
        "9m",
        "1p",
        "2p",
        "3p",
        "4p",
        "5p",
        "6p",
        "7p",
        "8p",
        "9p",
        "1s",
        "2s",
        "3s",
        "4s",
        "5s",
        "6s",
        "7s",
        "8s",
        "9s",
        "1z",
        "2z",
        "3z",
        "4z",
        "5z",
        "6z",
        "7z",
    ]
    return tiles[index]


def vec34_index_to_mjai_tile(index: int) -> str:
    """
    Vec34 index to mjai format

    Example:
        >>> vec34_index_to_tenhou_tile(0)
        "1m"
        >>> vec34_index_to_tenhou_tile(33)
        "C"
    """
    if index < 0 or index > 33:
        raise ValueError(f"index {index} is out of range [0, 33]")

    tiles = [
        "1m",
        "2m",
        "3m",
        "4m",
        "5m",
        "6m",
        "7m",
        "8m",
        "9m",
        "1p",
        "2p",
        "3p",
        "4p",
        "5p",
        "6p",
        "7p",
        "8p",
        "9p",
        "1s",
        "2s",
        "3s",
        "4s",
        "5s",
        "6s",
        "7s",
        "8s",
        "9s",
        "E",
        "S",
        "W",
        "N",
        "P",
        "F",
        "C",
    ]
    return tiles[index]
