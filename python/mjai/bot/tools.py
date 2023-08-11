from mjai.mlibriichi.tools import find_improving_tiles  # noqa, type: ignore


def convert_tehai_vec34_as_tenhou(
    tehai_vec34: list[int], akas_in_hand: list[bool] | None = None
) -> str:
    """
    Convert tehai_vec34 to tenhou.net/2 format

    NOTE: Open shapes are not supported.
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


def fmt_tenhou_call(ev: dict, player_id: int) -> str:
    if ev["type"] == "pon":
        rel_pos = (ev["target"] - player_id + 4) % 4
        call_tiles = [
            mjai_tile_to_tenhou(ev["pai"]),
            mjai_tile_to_tenhou(ev["consumed"][0]),
            mjai_tile_to_tenhou(ev["consumed"][1]),
        ]
        return "(p{}{}{})".format(
            deaka_tenhou_tile(call_tiles[0]),
            rel_pos,
            "r"
            if any([is_aka_tenhou_tile(tile) for tile in call_tiles])
            else "",
        )
    elif ev["type"] == "chi":
        color = ev["pai"][1]
        consecutive_nums = "".join(
            list(
                sorted(
                    [
                        mjai_tile_to_tenhou(ev["pai"])[0],
                        mjai_tile_to_tenhou(ev["consumed"][0])[0],
                        mjai_tile_to_tenhou(ev["consumed"][1])[0],
                    ]
                )
            )
        )
        called_tile_idx = 0
        if consecutive_nums[0] == mjai_tile_to_tenhou(ev["pai"])[0]:
            called_tile_idx = 0
        elif consecutive_nums[1] == mjai_tile_to_tenhou(ev["pai"])[0]:
            called_tile_idx = 1
        else:
            called_tile_idx = 2
        return f"({consecutive_nums}{color}{called_tile_idx})"
    else:
        # Not supported yet.
        return ""


def is_aka_tenhou_tile(tile: str) -> bool:
    return tile in ["0m", "0p", "0s"]


def deaka_tenhou_tile(tile: str) -> str:
    return f"5{tile[1]}" if is_aka_tenhou_tile(tile) else tile


def mjai_tile_to_tenhou(tile: str) -> str:
    mapping = {
        "5mr": "0m",
        "5pr": "0s",
        "5sr": "0p",
        "E": "1z",
        "S": "2z",
        "W": "3z",
        "N": "4z",
        "P": "5z",
        "F": "6z",
        "C": "7z",
    }
    return mapping.get(tile, tile)


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
