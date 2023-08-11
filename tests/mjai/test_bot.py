from mjai.bot import (
    RiichiBot,
    vec34_index_to_mjai_tile,
    vec34_index_to_tenhou_tile,
)
from mjai.mlibriichi.tools import find_improving_tiles  # type: ignore

from mjai import Bot


class MyBot(Bot):
    def __init__(self, player_id: int = 0):
        super().__init__(player_id)

    def think(self) -> str:
        return self.action_nothing()


def test_find_improving_tiles():
    player = Bot(player_id=0)
    assert (
        player.react(
            """[{"type":"start_game","names":["0","1","2","3"],"id":0}]"""
        )
        == '{"type":"none"}'
    )
    assert player.tehai_tenhou == ""

    assert (
        player.react(
            """[{"type":"start_kyoku","bakaze":"S","dora_marker":"1p","kyoku":2,"honba":2,"kyotaku":0,"oya":1,"scores":[800,61100,11300,26800],"tehais":[["4p","4s","P","3p","1p","5s","2m","F","1m","7s","9m","6m","9s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},{"type":"tsumo","actor":1,"pai":"?"},{"type":"dahai","actor":1,"pai":"F","tsumogiri":false},{"type":"tsumo","actor":2,"pai":"?"},{"type":"dahai","actor":2,"pai":"3m","tsumogiri":true},{"type":"tsumo","actor":3,"pai":"?"},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":true},{"type":"tsumo","actor":0,"pai":"3s"}]"""
        )
        == '{"type":"dahai","pai":"3s","actor":0,"tsumogiri":true}'
    )
    assert len(player.tehai_mjai) == 14

    ret = find_improving_tiles(player.tehai_tenhou)
    assert len(ret) == 6
    assert vec34_index_to_tenhou_tile(ret[0][0]) == "6m"
    assert vec34_index_to_tenhou_tile(ret[1][0]) == "9m"
    assert vec34_index_to_tenhou_tile(ret[2][0]) == "1p"
    assert vec34_index_to_tenhou_tile(ret[3][0]) == "4p"
    assert vec34_index_to_tenhou_tile(ret[4][0]) == "5z"
    assert vec34_index_to_tenhou_tile(ret[5][0]) == "6z"
    assert vec34_index_to_mjai_tile(ret[3][0]) == "4p"
    assert vec34_index_to_mjai_tile(ret[4][0]) == "P"
    assert vec34_index_to_mjai_tile(ret[5][0]) == "F"


def test_tsumogiri_bot():
    player = Bot(player_id=0)
    assert (
        player.react(
            """[{"type":"start_game","names":["0","1","2","3"],"id":0}]"""
        )
        == '{"type":"none"}'
    )
    assert player.tehai_tenhou == ""

    assert (
        player.react(
            """[{"type":"start_kyoku","bakaze":"S","dora_marker":"1p","kyoku":2,"honba":2,"kyotaku":0,"oya":1,"scores":[800,61100,11300,26800],"tehais":[["4p","4s","P","3p","1p","5s","2m","F","1m","7s","9m","6m","9s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},{"type":"tsumo","actor":1,"pai":"?"},{"type":"dahai","actor":1,"pai":"F","tsumogiri":false},{"type":"tsumo","actor":2,"pai":"?"},{"type":"dahai","actor":2,"pai":"3m","tsumogiri":true},{"type":"tsumo","actor":3,"pai":"?"},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":true},{"type":"tsumo","actor":0,"pai":"3s"}]"""
        )
        == '{"type":"dahai","pai":"3s","actor":0,"tsumogiri":true}'
    )
    assert len(player.tehai_mjai) == 14
    assert player.tehai_tenhou == "1269m134p34579s56z"
    assert player.is_oya is False
    assert player.last_self_tsumo == "3s"
    assert player.can_discard is True
    assert player.honba == 2
    assert player.kyoku == 2
    assert player.last_kawa_tile == "1m"


def test_custom_bot():
    player = MyBot(player_id=0)
    assert (
        player.react(
            """[{"type":"start_game","names":["0","1","2","3"],"id":0}]"""
        )
        == '{"type":"none"}'
    )
    assert (
        player.react(
            """[{"type":"start_kyoku","bakaze":"S","dora_marker":"1p","kyoku":2,"honba":2,"kyotaku":0,"oya":1,"scores":[800,61100,11300,26800],"tehais":[["4p","4s","P","3p","1p","5s","2m","F","1m","7s","9m","6m","9s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},{"type":"tsumo","actor":1,"pai":"?"},{"type":"dahai","actor":1,"pai":"F","tsumogiri":false},{"type":"tsumo","actor":2,"pai":"?"},{"type":"dahai","actor":2,"pai":"3m","tsumogiri":true},{"type":"tsumo","actor":3,"pai":"?"},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":true},{"type":"tsumo","actor":0,"pai":"3s"}]"""
        )
        == '{"type":"none"}'
    )
