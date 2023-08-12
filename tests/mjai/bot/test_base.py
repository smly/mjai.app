import json

from mjai import Bot


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
            json.dumps(
                [
                    {
                        "type": "start_kyoku",
                        "bakaze": "S",
                        "dora_marker": "1p",
                        "kyoku": 2,
                        "honba": 2,
                        "kyotaku": 0,
                        "oya": 1,
                        "scores": [800, 61100, 11300, 26800],
                        "tehais": [
                            "4p 4s P 3p 1p 5s 2m F 1m 7s 9m 6m 9s".split(),
                            "? ? ? ? ? ? ? ? ? ? ? ? ?".split(),
                            "? ? ? ? ? ? ? ? ? ? ? ? ?".split(),
                            "? ? ? ? ? ? ? ? ? ? ? ? ?".split(),
                        ],
                    },
                    {"type": "tsumo", "actor": 1, "pai": "?"},
                    {
                        "type": "dahai",
                        "actor": 1,
                        "pai": "F",
                        "tsumogiri": False,
                    },
                    {"type": "tsumo", "actor": 2, "pai": "?"},
                    {
                        "type": "dahai",
                        "actor": 2,
                        "pai": "3m",
                        "tsumogiri": True,
                    },
                    {"type": "tsumo", "actor": 3, "pai": "?"},
                    {
                        "type": "dahai",
                        "actor": 3,
                        "pai": "1m",
                        "tsumogiri": True,
                    },
                    {"type": "tsumo", "actor": 0, "pai": "3s"},
                ]
            )
        )
        == '{"type":"dahai","pai":"3s","actor":0,"tsumogiri":true}'
    )
    assert len(player.tehai_mjai) == 14


def test_tsumogiri_bot():
    bot = Bot(player_id=0)
    assert (
        bot.react(
            """[{"type":"start_game","names":["0","1","2","3"],"id":0}]"""
        )
        == '{"type":"none"}'
    )
    assert bot.tehai_tenhou == ""

    assert (
        bot.react(
            """
            [{"type":"start_kyoku","bakaze":"S","dora_marker":"1p","kyoku":2,
            "honba":2,"kyotaku":1,"oya":1,"scores":[800,61100,11300,26800],
            "tehais":
            [["4p","4s","P","3p","1p","5s","2m","F","1m","7s","9m","6m","9s"],
            ["?","?","?","?","?","?","?","?","?","?","?","?","?"],
            ["?","?","?","?","?","?","?","?","?","?","?","?","?"],
            ["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},
            {"type":"tsumo","actor":1,"pai":"?"},
            {"type":"dahai","actor":1,"pai":"F","tsumogiri":false},
            {"type":"tsumo","actor":2,"pai":"?"},
            {"type":"dahai","actor":2,"pai":"3m","tsumogiri":true},
            {"type":"tsumo","actor":3,"pai":"?"},
            {"type":"dahai","actor":3,"pai":"1m","tsumogiri":true},
            {"type":"tsumo","actor":0,"pai":"3s"}]""".replace(
                "\n", ""
            ).strip()
        )
        == '{"type":"dahai","pai":"3s","actor":0,"tsumogiri":true}'
    )
    assert len(bot.tehai_mjai) == 14
    assert (
        bot.tehai_tenhou == "1269m134p34579s56z"
    )  # NOTE: state just before last own reaction
    assert bot.is_oya is False
    assert bot.last_self_tsumo == "3s"
    assert bot.can_discard is True
    assert bot.honba == 2
    assert bot.kyoku == 2
    assert bot.kyotaku == 1
    assert bot.last_kawa_tile == "1m"

    assert bot.scores == [800, 61100, 11300, 26800]
    assert bot.jikaze == "N"
    assert bot.bakaze == "S"
    assert bot.player_state.at_furiten is False
    assert len(bot.tiles_seen) == 34
    assert len(bot.forbidden_tiles) == 34
    assert bot.tiles_seen["F"] == 2
    assert bot.tiles_seen["1p"] == 2
    assert (
        bot.discarded_tiles(0) == []
    )  # NOTE: state just before last own reaction

    assert bot.get_call_events(0) == []
    assert len(bot.dora_indicators) == 1
    assert bot.dora_indicators[0] == "1p"


class MyBot(Bot):
    def __init__(self, player_id: int = 0):
        super().__init__(player_id)

    def think(self) -> str:
        return self.action_nothing()


def test_custom_bot():
    player = MyBot(player_id=0)
    assert (
        player.react(
            """[{"type":"start_game","names":["0","1","2","3"],"id":0}]"""
        )
        == '{"type":"none"}'
    )
    assert player.tehai_tenhou == ""

    assert (
        player.react(
            """
            [{"type":"start_kyoku","bakaze":"S","dora_marker":"1p","kyoku":2,
            "honba":2,"kyotaku":0,"oya":1,"scores":[800,61100,11300,26800],
            "tehais":
            [["4p","4s","P","3p","1p","5s","2m","F","1m","7s","9m","6m","9s"],
            ["?","?","?","?","?","?","?","?","?","?","?","?","?"],
            ["?","?","?","?","?","?","?","?","?","?","?","?","?"],
            ["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},
            {"type":"tsumo","actor":1,"pai":"?"},
            {"type":"dahai","actor":1,"pai":"F","tsumogiri":false},
            {"type":"tsumo","actor":2,"pai":"?"},
            {"type":"dahai","actor":2,"pai":"3m","tsumogiri":true},
            {"type":"tsumo","actor":3,"pai":"?"},
            {"type":"dahai","actor":3,"pai":"1m","tsumogiri":true},
            {"type":"tsumo","actor":0,"pai":"P"}]""".replace(
                "\n", ""
            ).strip()
        )
        == '{"type":"none"}'
    )
    assert player.last_kawa_tile == "1m"
    assert player.last_self_tsumo == "P"
    assert player.tehai_tenhou == "1269m134p4579s556z"
