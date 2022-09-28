import json
from typing import Any

import mjx
from mjx.tile import Tile
from mjx.const import TileType, EventType
from mjx.agents import (
    RuleBasedAgent,
    ShantenAgent,
)
import mjxproto


def to_mjx_tile(tile_str: str, ignore_aka: bool = False) -> int:
    match tile_str:
        case "1m": return 0
        case "2m": return 4
        case "3m": return 8
        case "4m": return 12
        case "5mr": return 16
        case "5m": return (16 if ignore_aka else 17)
        case "6m": return 20
        case "7m": return 24
        case "8m": return 28
        case "9m": return 32
        case "1p": return 36
        case "2p": return 40
        case "3p": return 44
        case "4p": return 48
        case "5pr": return 52
        case "5p": return (52 if ignore_aka else 53)
        case "6p": return 56
        case "7p": return 60
        case "8p": return 64
        case "9p": return 68
        case "1s": return 72
        case "2s": return 76
        case "3s": return 80
        case "4s": return 84
        case "5sr": return 88
        case "5s": return (88 if ignore_aka else 89)
        case "6s": return 92
        case "7s": return 96
        case "8s": return 100
        case "9s": return 104
        case "E": return 108
        case "S": return 112
        case "W": return 116
        case "N": return 120
        case "P": return 124
        case "F": return 128
        case "C": return 132


def to_mjai_tile(tile_id: int) -> str:
    tile = Tile(tile_id)
    tile_type = tile.type()
    tile_num = tile.num()
    match tile_type:
        case TileType.M1: return "1m"
        case TileType.M2: return "2m"
        case TileType.M3: return "3m"
        case TileType.M4: return "4m"
        case TileType.M5: return "5mr" if tile.is_red() else "5m"
        case TileType.M6: return "6m"
        case TileType.M7: return "7m"
        case TileType.M8: return "8m"
        case TileType.M9: return "9m"
        case TileType.P1: return "1p"
        case TileType.P2: return "2p"
        case TileType.P3: return "3p"
        case TileType.P4: return "4p"
        case TileType.P5: return "5pr" if tile.is_red() else "5p"
        case TileType.P6: return "6p"
        case TileType.P7: return "7p"
        case TileType.P8: return "8p"
        case TileType.P9: return "9p"
        case TileType.S1: return "1s"
        case TileType.S2: return "2s"
        case TileType.S3: return "3s"
        case TileType.S4: return "4s"
        case TileType.S5: return "5sr" if tile.is_red() else "5s"
        case TileType.S6: return "6s"
        case TileType.S7: return "7s"
        case TileType.S8: return "8s"
        case TileType.S9: return "9s"
        case TileType.EW: return "E"
        case TileType.SW: return "S"
        case TileType.WW: return "W"
        case TileType.NW: return "N"
        case TileType.WD: return "P"
        case TileType.GD: return "F"
        case TileType.RD: return "C"

    raise ValueEerror(f"Invalid tile_id: {tile_id}")


def json_dumps(json_data):
    return json.dumps(json_data, separators=(",", ":"))


class OpenCodeGen:
    def __init__(self):
        pass

    @staticmethod
    def from_mjai_kan(ev: dict[str, Any], obs: dict[str, Any]) -> tuple[int, list[int]]:
        pai = ev["consumed"][0]
        base = to_mjx_tile(pai, ignore_aka=True) // 4

        if "target" in ev:
            # daiminkan
            rel_pos = (ev["target"] - ev["actor"] + 4) % 4
            called = 3
        else:
            # ankan
            rel_pos = 0
            called = 0

        value = rel_pos
        value += ((base * 4 + called) << 8)

        new_op = mjx.open.Open(value)
        consume_tiles_from_hand = [t.id() for t in new_op.tiles_from_hand()]

        return value, consume_tiles_from_hand

    @staticmethod
    def from_mjai_kakan(ev: dict[str, Any], obs: dict[str, Any]) -> tuple[int, list[int], int, int]:
        pai_base = to_mjx_tile(ev['pai'], ignore_aka=True) // 4

        if ev["actor"] == obs["who"]:
            # 自家の対応する open を探す
            op = None
            for open_code in obs["privateObservation"]["currHand"]["opens"]:
                op = mjx.open.Open(open_code)
                open_pai_base = op.tiles()[0].id() // 4
                if pai_base == open_pai_base:
                    break
        else:
            # 他家
            op = None
            for event in obs["publicObservation"]["events"]:
                if "type" in event and event["type"] == "EVENT_TYPE_PON":
                    open_code = event["open"]
                    op = mjx.open.Open(open_code)
                    open_pai_base = op.tiles()[0].id() // 4
                    if pai_base == open_pai_base:
                        break

        assert op is not None

        # pon flag を削除して kan flag を立てる
        value = ((0xffff ^ (1 << 3)) & op.bit) | (1 << 4)

        new_op = mjx.open.Open(value)
        consume_tiles_from_hand = [t.id() for t in new_op.tiles_from_hand()]
        called_tile_id = new_op.last_tile().id()

        return value, consume_tiles_from_hand, called_tile_id, op.bit

    @staticmethod
    def from_mjai_pon(ev: dict[str, Any], obs: dict[str, Any]) -> tuple[int, list[int]]:
        pai = ev["pai"]
        base = to_mjx_tile(pai, ignore_aka=True)
        base_lowest = base // 4

        called_tile = obs["publicObservation"]["events"][-1]["tile"] - base
        called = 2
        if pai[-1] == "r":
            called = 0

        if ev["actor"] == obs["who"]:
            consume_tiles_from_hand = [
                t for t in obs["privateObservation"]["currHand"]["closedTiles"]
                if to_mjx_tile(to_mjai_tile(t), ignore_aka=True) == base
            ][:2]

            available_codes = [0, 1, 2, 3]
            for t in consume_tiles_from_hand[:2]:
                available_codes.remove(t - base)
            available_codes.remove(called_tile)
            not_pon = available_codes[0]  # pon していない牌
        else:
            not_consume_tiles_from_hand = [
                t for t in obs["privateObservation"]["currHand"]["closedTiles"]
                if to_mjx_tile(to_mjai_tile(t), ignore_aka=True) == base
            ] + [
                t for t in obs["publicObservation"]["doraIndicators"]
                if to_mjx_tile(to_mjai_tile(t), ignore_aka=True) == base
            ]

            candidates = [
                0 + to_mjx_tile(ev['pai'], ignore_aka=True),
                1 + to_mjx_tile(ev['pai'], ignore_aka=True),
                2 + to_mjx_tile(ev['pai'], ignore_aka=True),
                3 + to_mjx_tile(ev['pai'], ignore_aka=True),
            ]
            candidates.remove(called_tile + base)
            for t in not_consume_tiles_from_hand:
                candidates.remove(t)

            for e in obs["publicObservation"]["events"][:-1]:
                if e not in ['tile', 'open']:
                    continue
                e = mjx.Event(e)
                if e.type() == EventType.EVENT_TYPE_DRAW:
                    t = e.tile().id()
                    if t in candidates:
                        candidates.remove(t)
                elif e.type() == EventType.EVENT_TYPE_CHI:
                    for t in e.open().tiles():
                        t = t.id()
                        if t in candidates:
                            candidates.remove(t)
                elif e.type() == EventType.EVENT_TYPE_PON:
                    for t in e.open().tiles():
                        t = t.id()
                        if t in candidates:
                            candidates.remove(t)

            consume_tiles_from_hand = candidates[:2]

            available_codes = [0, 1, 2, 3]
            for t in consume_tiles_from_hand[:2]:
                available_codes.remove(t - base)
            available_codes.remove(called_tile)
            not_pon = available_codes[0]  # pon していない牌

        rel_pos = (ev["target"] - ev["actor"] + 4) % 4
        value = rel_pos
        value += (1 << 3)
        value += (not_pon << 5)  # not pon
        value += ((base_lowest * 3 + called) << 9)
        return value, consume_tiles_from_hand

    @staticmethod
    def from_mjai_chi(ev: dict[str, Any], obs: dict[str, Any]):
        pai = ev['pai']
        consumed = ev['consumed']
        rel_pos = (ev["target"] - ev["actor"] + 4) % 4

        base = min([
            to_mjx_tile(pai, ignore_aka=True),
            to_mjx_tile(consumed[0], ignore_aka=True),
            to_mjx_tile(consumed[1], ignore_aka=True),
        ])

        # Which tile out of the three was called
        tile_from_last_event = obs["publicObservation"]["events"][-1]["tile"]
        called = (to_mjx_tile(pai, ignore_aka=True) - base) // 4

        if ev["actor"] == obs["who"]:
            consume0_candidates = [
                t for t in obs["privateObservation"]["currHand"]["closedTiles"]
                if (t // 4) == (to_mjx_tile(consumed[0], ignore_aka=True) // 4)
            ]
            consume0 = consume0_candidates[0]
            consume1_candidates = [
                t for t in obs["privateObservation"]["currHand"]["closedTiles"]
                if (t // 4) == (to_mjx_tile(consumed[1], ignore_aka=True) // 4)
            ]
            consume1 = consume1_candidates[0]
        else:
            if consumed[0].endswith('r'):
                consume0 = to_mjx_tile(consumed[0])
            else:
                consume0_base = to_mjx_tile(consumed[0])
                consume0_candidates = [
                    0 + consume0_base,
                    1 + consume0_base,
                    2 + consume0_base,
                    3 + consume0_base,
                ]
                if consumed[0].startswith('5'):
                    consume0_candidates.remove(consume0_base)  # 赤ドラを除外する

                for t in obs["privateObservation"]["initHand"]["closedTiles"]:
                    if t in consume0_candidates:
                        consume0_candidates.remove(t)
                for e in obs["publicObservation"]["events"]:
                    if e not in ['tile', 'open']:
                        continue
                    e = mjx.Event(e)
                    if e.type() == EventType.EVENT_TYPE_DRAW:
                        t = e.tile().id()
                        if t in consume0_candidates:
                            consume0_candidates.remove(t)
                    elif e.type() == EventType.EVENT_TYPE_CHI:
                        for t in e.open().tiles():
                            t = t.id()
                            if t in consume0_candidates:
                                consume0_candidates.remove(t)
                    elif e.type() == EventType.EVENT_TYPE_PON:
                        for t in e.open().tiles():
                            t = t.id()
                            if t in consume0_candidates:
                                consume0_candidates.remove(t)
                consume0 = consume0_candidates[0]

            # ２個目の消費（他家の鳴き）
            if consumed[1].endswith('r'):
                consume1 = to_mjx_tile(consumed[1])
            else:
                consume1_base = to_mjx_tile(consumed[1])
                consume1_candidates = [
                    0 + consume1_base,
                    1 + consume1_base,
                    2 + consume1_base,
                    3 + consume1_base,
                ]
                if consumed[1].startswith('5'):
                    consume1_candidates.remove(consume1_base)  # 赤ドラを除外する

                for t in obs["privateObservation"]["initHand"]["closedTiles"]:
                    if t in consume1_candidates:
                        consume1_candidates.remove(t)
                for e in obs["publicObservation"]["events"]:
                    if e not in ['tile', 'open']:
                        continue
                    e = mjx.Event(e)
                    if e.type() == EventType.EVENT_TYPE_DRAW:
                        t = e.tile().id()
                        if t in consume1_candidates:
                            consume1_candidates.remove(t)
                    elif e.type() == EventType.EVENT_TYPE_CHI:
                        for t in e.open().tiles():
                            t = t.id()
                            if t in consume1_candidates:
                                consume1_candidates.remove(t)
                    elif e.type() == EventType.EVENT_TYPE_PON:
                        for t in e.open().tiles():
                            t = t.id()
                            if t in consume1_candidates:
                                consume1_candidates.remove(t)
                consume1 = consume1_candidates[0]

        # pai, consumed に赤ドラがある場合のために ignore_aka=True と比較する
        if called == 0:
            called_base = to_mjx_tile(ev['pai'])
            t0 = obs["publicObservation"]["events"][-1]["tile"] - called_base
            t1 = consume0 - to_mjx_tile(consumed[0], ignore_aka=True)
            t2 = consume1 - to_mjx_tile(consumed[1], ignore_aka=True)
        elif called == 1:
            called_base = to_mjx_tile(ev['pai'])
            t1 = obs["publicObservation"]["events"][-1]["tile"] - called_base
            t0 = consume0 - to_mjx_tile(consumed[0], ignore_aka=True)
            t2 = consume1 - to_mjx_tile(consumed[1], ignore_aka=True)
        else:
            called_base = to_mjx_tile(ev['pai'])
            t2 = obs["publicObservation"]["events"][-1]["tile"] - called_base
            t0 = consume0 - to_mjx_tile(consumed[0], ignore_aka=True)
            t1 = consume1 - to_mjx_tile(consumed[1], ignore_aka=True)

        base_lowest = base // 4
        value = ((base_lowest // 9) * 7 + base_lowest % 9) * 3 + called
        value = value << 10
        value += (t2 << 7)
        value += (t1 << 5)
        value += (t0 << 3)
        value += (1 << 2)
        value += rel_pos
        return value, [consume0, consume1]


class MjxGateway:
    def __init__(self, actor_id, mjx_bot):
        self.actor_id = actor_id
        self.mjx_bot = mjx_bot
        self.base_obs = {}
        self.hai_offset = {}

    def get_obs_open(self) -> list[int]:
        if len(self.base_obs) == 0:
            raise ValueError("Kyoku not started.")
        return self.base_obs["privateObservation"]["currHand"]["opens"]

    def get_obs_hand(self) -> list[int]:
        if len(self.base_obs) == 0:
            raise ValueError("Kyoku not started.")
        return self.base_obs["privateObservation"]["currHand"]["closedTiles"]

    def get_obs(self) -> dict[str, Any]:
        return self.base_obs

    def set_obs_offset(self, base_obs, hai_offset) -> None:
        self.base_obs = base_obs
        self.hai_offset = hai_offset

    def get_legal_actions(self) -> list[Any]:
        obs = mjx.Observation(json.dumps(self.base_obs.copy()))
        return obs.legal_actions()

    def _get_mjx_obs(self, mjai_events):
        # 1. MJAI の入力を MJX に変換して Game Client に渡す
        for mjai_event in mjai_events:
            mjai_event_type = mjai_event.get("type")

            match mjai_event_type:
                case "start_kyoku":
                    tehais = [to_mjx_tile(s) for s in mjai_event["tehais"][self.actor_id]]

                    # Initialize hai_offset
                    self.hai_offset = {}
                    self.hai_offset[to_mjx_tile(mjai_event["dora_marker"])] = 1
                    for i, hai in enumerate(tehais):
                        tehais[i] += self.hai_offset.get(hai, 0)
                        self.hai_offset[hai] = self.hai_offset.get(hai, 0) + 1

                    self.base_obs = {
                        "who": self.actor_id,
                        "publicObservation": {
                            "playerIds": ["player_0","player_1","player_2","player_3"],
                            "initScore": {
                                "tens": mjai_event["scores"],
                            },
                            "doraIndicators": [
                                to_mjx_tile(mjai_event["dora_marker"])
                            ],
                            "events": [],
                        },
                        "privateObservation": {
                            "who": self.actor_id,
                            "initHand": {
                                "closedTiles": tehais,
                            },
                            "drawHistory": [],
                            "currHand": {
                                "closedTiles": list(sorted(tehais)),
                                "opens": [],
                            }
                        }
                    }

                case "tsumo":

                    if self.actor_id == mjai_event["actor"]:
                        hai = to_mjx_tile(mjai_event["pai"])
                        hai_ = hai + self.hai_offset.get(hai, 0)
                        self.hai_offset[hai] = self.hai_offset.get(hai, 0) + 1

                        # Update obs
                        self.base_obs["privateObservation"]["drawHistory"].append(hai_)
                        self.base_obs["privateObservation"]["currHand"]["closedTiles"].append(hai_)
                        self.base_obs["privateObservation"]["currHand"]["closedTiles"] = list(sorted(
                            self.base_obs["privateObservation"]["currHand"]["closedTiles"]
                        ))

                    # Add event
                    row = {"type": "EVENT_TYPE_DRAW"}
                    if mjai_event["actor"] > 0:
                        row["who"] = mjai_event["actor"]

                    self.base_obs["publicObservation"]["events"].append(row)

                case "dahai":
                    hai = to_mjx_tile(mjai_event["pai"])

                    if self.actor_id == mjai_event["actor"]:
                        remove_candidates = [
                            t for t in self.base_obs["privateObservation"]["currHand"]["closedTiles"]
                            if to_mjx_tile(to_mjai_tile(t)) == hai
                        ]
                        hai_ = remove_candidates[0]

                        # Update obs
                        self.base_obs["privateObservation"]["currHand"]["closedTiles"].remove(hai_)

                    else:
                        # 自分ではない場合、新規に出現するため hai をインクリメントする
                        hai_ = hai + self.hai_offset.get(hai, 0)
                        self.hai_offset[hai] = self.hai_offset.get(hai, 0) + 1

                    row = {
                        "tile": hai_,
                    }
                    if mjai_event["actor"] > 0:
                        row["who"] = mjai_event["actor"]
                    self.base_obs["publicObservation"]["events"].append(row)

                case "chi":
                    open_code, consume_tiles_from_hand = OpenCodeGen.from_mjai_chi(
                        mjai_event, self.base_obs
                    )

                    if self.actor_id == mjai_event["actor"]:
                        # Update obs
                        self.base_obs["privateObservation"]["currHand"]["opens"].append(open_code)
                        for t in consume_tiles_from_hand:
                            self.base_obs["privateObservation"]["currHand"]["closedTiles"].remove(t)

                    row = {
                        "type": "EVENT_TYPE_CHI",
                        "open": open_code,
                    }
                    if mjai_event["actor"] > 0:
                        row["who"] = mjai_event["actor"]

                    self.base_obs["publicObservation"]["events"].append(row)

                case "pon":
                    open_code, consume_tiles_from_hand = OpenCodeGen.from_mjai_pon(
                        mjai_event, self.base_obs)

                    if self.actor_id == mjai_event["actor"]:
                        # Update obs
                        self.base_obs["privateObservation"]["currHand"]["opens"].append(open_code)
                        for t in consume_tiles_from_hand:
                            self.base_obs["privateObservation"]["currHand"]["closedTiles"].remove(t)

                    row = {
                        "type": "EVENT_TYPE_PON",
                        "open": open_code,
                    }
                    if mjai_event["actor"] > 0:
                        row["who"] = mjai_event["actor"]

                    self.base_obs["publicObservation"]["events"].append(row)

                case "reach":
                    row = {
                        "type": "EVENT_TYPE_RIICHI",
                        "who": mjai_event["actor"],
                    }
                    self.base_obs["publicObservation"]["events"].append(row)

                case "ankan":
                    open_code, consume_tiles_from_hand = OpenCodeGen.from_mjai_kan(
                        mjai_event, self.base_obs)

                    if self.actor_id == mjai_event["actor"]:
                        # Update obs
                        self.base_obs["privateObservation"]["currHand"]["opens"].append(open_code)
                        for t in consume_tiles_from_hand:
                            self.base_obs["privateObservation"]["currHand"]["closedTiles"].remove(t)

                    row = {
                        "type": "EVENT_TYPE_CLOSED_KAN",
                        "open": open_code,
                    }
                    if mjai_event["actor"] > 0:
                        row["who"] = mjai_event["actor"]

                    self.base_obs["publicObservation"]["events"].append(row)

                case "kakan":
                    open_code, consume_tiles_from_hand, called_tile_id, pon_open_code = OpenCodeGen.from_mjai_kakan(
                        mjai_event, self.base_obs)

                    if self.actor_id == mjai_event["actor"]:
                        # Update obs
                        self.base_obs["privateObservation"]["currHand"]["opens"].append(open_code)
                        self.base_obs["privateObservation"]["currHand"]["opens"].remove(pon_open_code)
                        self.base_obs["privateObservation"]["currHand"]["closedTiles"].remove(called_tile_id)

                    row = {
                        "type": "EVENT_TYPE_ADDED_KAN",
                        "open": open_code,
                    }

                    if mjai_event["actor"] > 0:
                        row["who"] = mjai_event["actor"]

                    self.base_obs["publicObservation"]["events"].append(row)

                case "daiminkan":
                    open_code, consume_tiles_from_hand = OpenCodeGen.from_mjai_kan(
                        mjai_event, self.base_obs)

                    if self.actor_id == mjai_event["actor"]:
                        # Update obs
                        self.base_obs["privateObservation"]["currHand"]["opens"].append(open_code)
                        for t in consume_tiles_from_hand:
                            self.base_obs["privateObservation"]["currHand"]["closedTiles"].remove(t)

                    row = {
                        "type": "EVENT_TYPE_OPEN_KAN",
                        "open": open_code,
                    }
                    if mjai_event["actor"] > 0:
                        row["who"] = mjai_event["actor"]

                    self.base_obs["publicObservation"]["events"].append(row)

                case "reach_accepted":
                    pass

                case _:
                    # self.base_obs に変更を行わない
                    continue

        # legal action を付与する
        obs_json = self.base_obs.copy()
        obs = mjx.Observation(json.dumps(obs_json))
        obs_json = mjx.Observation.add_legal_actions(json.dumps(obs_json, separators=(",", ":")))

        # legal action を付与した上で act を呼ぶ
        obs = mjx.Observation(obs_json)

        for action in obs.legal_actions():
            if action.to_json().startswith('{"tile":'):
                t_ = to_mjai_tile(json.loads(action.to_json())["tile"])

        return obs

    def _get_mjai_response(self, mjx_action):
        """
        MJX の Action を MJAI に変換する

        ACTION_TYPE_* のすべてのパターンに対する挙動を定義する
        https://github.com/mjx-project/mjx/blob/1a120f748151b64becd41448cd43165e23302cc2/mjx/const.py#L6
        - [X] DISCARD = mjxproto.ACTION_TYPE_DISCARD
        - [X] TSUMOGIRI = mjxproto.ACTION_TYPE_TSUMOGIRI
        - [X] RIICHI = mjxproto.ACTION_TYPE_RIICHI
        - [X] CLOSED_KAN = mjxproto.ACTION_TYPE_CLOSED_KAN
        - [X] ADDED_KAN = mjxproto.ACTION_TYPE_ADDED_KAN
        - [X] TSUMO = mjxproto.ACTION_TYPE_TSUMO
        - [X] ABORTIVE_DRAW_NINE_TERMINALS = mjxproto.ACTION_TYPE_ABORTIVE_DRAW_NINE_TERMINALS  # 九種九牌
        - [X] CHI = mjxproto.ACTION_TYPE_CHI
        - [X] PON = mjxproto.ACTION_TYPE_PON
        - [X] OPEN_KAN = mjxproto.ACTION_TYPE_OPEN_KAN
        - [X] RON = mjxproto.ACTION_TYPE_RON
        - [X] PASS = mjxproto.ACTION_TYPE_NO
        - [X] DUMMY = mjxproto.ACTION_TYPE_DUMMY

        """
        action_json = json.loads(mjx_action.to_json())

        match mjx_action.type():
            case mjxproto.ACTION_TYPE_DISCARD | mjxproto.ACTION_TYPE_TSUMOGIRI:
                is_tsumogiri = mjx_action.type() == mjxproto.ACTION_TYPE_TSUMOGIRI
                return json_dumps({
                    "type": "dahai",
                    "actor": self.actor_id,
                    "pai": to_mjai_tile(action_json.get("tile", 0)),
                    "tsumogiri": is_tsumogiri
                })

            case mjxproto.ACTION_TYPE_RIICHI:
                return json_dumps({
                    "type": "reach",
                    "actor": self.actor_id,
                })

            case mjxproto.ACTION_TYPE_CLOSED_KAN:
                open_ = mjx_action.open()
                assert open_ is not None
                consumed = open_.tiles_from_hand()
                stolen_tile = open_.stolen_tile()

                return json_dumps({
                    "type": "ankan",
                    "actor": mjx_action.who(),
                    "target": (mjx_action.who() + open_.steal_from()) % 4,
                    "consumed": [to_mjai_tile(tile.id()) for tile in consumed],
                })

            case mjxproto.ACTION_TYPE_ADDED_KAN:
                open_ = mjx_action.open()
                assert open_ is not None
                pai = to_mjai_tile(open_.last_tile().id())
                consumed = open_.tiles_from_hand()

                return json_dumps({
                    "type": "kakan",
                    "actor": self.actor_id,
                    "pai": pai,
                    "consumed": [to_mjai_tile(tile.id()) for tile in consumed],
                })

            case mjxproto.ACTION_TYPE_TSUMO:
                return json_dumps({
                    "type": "hora",
                    "actor": self.actor_id,
                    "target": self.actor_id,
                })

            case mjxproto.ACTION_TYPE_ABORTIVE_DRAW_NINE_TERMINALS:
                return json_dumps({
                    "type":"ryukyoku",
                    "actor": self.actor_id,
                })

            case mjxproto.ACTION_TYPE_OPEN_KAN:
                open_ = mjx_action.open()
                assert open_ is not None
                consumed = open_.tiles_from_hand()
                stolen_tile = open_.stolen_tile()

                return json_dumps({
                    "type": "daiminkan",
                    "actor": mjx_action.who(),
                    "target": (mjx_action.who() + open_.steal_from()) % 4,
                    "pai": to_mjai_tile(stolen_tile.id()),
                    "consumed": [to_mjai_tile(tile.id()) for tile in consumed],
                })

            case mjxproto.ACTION_TYPE_RON:
                return json_dumps({
                    "type": "hora",
                    "pai": to_mjai_tile(action_json.get("tile", 0)),
                    "actor": self.actor_id,
                    "target": self.base_obs["publicObservation"]["events"][-1].get("who", 0),
                })

            case mjxproto.ACTION_TYPE_CHI:
                open_ = mjx_action.open()
                assert open_ is not None
                consumed = open_.tiles_from_hand()
                stolen_tile = open_.stolen_tile()

                return json_dumps({
                    "type": "chi",
                    "actor": mjx_action.who(),
                    "target": (mjx_action.who() + open_.steal_from()) % 4,
                    "pai": to_mjai_tile(stolen_tile.id()),
                    "consumed": [to_mjai_tile(tile.id()) for tile in consumed],
                })

            case mjxproto.ACTION_TYPE_PON:
                open_ = mjx_action.open()
                assert open_ is not None
                consumed = open_.tiles_from_hand()
                stolen_tile = open_.stolen_tile()

                return json_dumps({
                    "type": "pon",
                    "actor": mjx_action.who(),
                    "target": (mjx_action.who() + open_.steal_from()) % 4,
                    "pai": to_mjai_tile(stolen_tile.id()),
                    "consumed": [to_mjai_tile(tile.id()) for tile in consumed],
                })

            case mjxproto.ACTION_TYPE_NO | mjxproto.ACTION_TYPE_DUMMY:
                return json_dumps({"type": "none"})

        return json_dumps({"type": "none"})

    def react(self, events_str: str) -> str:
        events: list[dict[str, Any]] = json.loads(events_str)

        # 空ではないリストが与えられる
        assert len(events) > 0

        # 最後のイベントの `type` によって分岐する
        if events[-1]["type"] in ["start_game", "end_kyoku", "end_game"]:
            return json_dumps({"type": "none"})
        else:
            # 1. MJAI の入力を MJX に変換して Game Client に渡す
            # 2. MJX の Action を MJAI に変換する
            obs = self._get_mjx_obs(events)
            mjx_action = self.mjx_bot.act(obs)
            return self._get_mjai_response(mjx_action)
