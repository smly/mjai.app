from mjai.bot.rulebase import RulebaseBot


def fmt(events_str: str):
    return events_str.replace("\n", "").strip()


def test_custom_bot():
    player = RulebaseBot(player_id=0)

    assert (
        player.react(
            """[{"type":"start_game","names":["0","1","2","3"],"id":0}]"""
        )
        == '{"type":"none"}'
    )

    assert (
        player.react(
            fmt(
                """
                    [{"type":"start_kyoku","bakaze":"S","dora_marker":"1p","kyoku":2,
                    "honba":2,"kyotaku":0,"oya":1,"scores":[800,61100,11300,26800],
                    "tehais":
                    [["4p","4s","6s","3p","1p","5s","2m","F","1m","7s","9m","P","P"],
                    ["?","?","?","?","?","?","?","?","?","?","?","?","?"],
                    ["?","?","?","?","?","?","?","?","?","?","?","?","?"],
                    ["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},
                    {"type":"tsumo","actor":1,"pai":"?"},
                    {"type":"dahai","actor":1,"pai":"F","tsumogiri":false},
                    {"type":"tsumo","actor":2,"pai":"?"},
                    {"type":"dahai","actor":2,"pai":"3m","tsumogiri":true},
                    {"type":"tsumo","actor":3,"pai":"?"},
                    {"type":"dahai","actor":3,"pai":"P","tsumogiri":true}
                    ]
                """
            )
        )
        == '{"type":"pon","actor":0,"target":3,"pai":"P","consumed":["P","P"]}'
    )
    assert player.last_kawa_tile == "P"
    assert player.last_self_tsumo == ""  # No tsumo events yet
    assert player.tehai_tenhou == "129m134p4567s556z"

    assert (
        player.react(
            fmt(
                """
                [{"type":"pon","actor":0,"target":3,"pai":"P","consumed":["P","P"]}]
                """
            )
        )
        == '{"type":"dahai","pai":"9m","actor":0,"tsumogiri":false}'
    )
    assert player.tehai_tenhou == "129m134p4567s6z(p5z3)"

    assert (
        player.react(
            fmt(
                """
                [{"type":"dahai","actor":0,"pai":"9m","tsumogiri":false},
                {"type":"tsumo","actor":1,"pai":"?"},
                {"type":"dahai","actor":1,"pai":"F","tsumogiri":false},
                {"type":"tsumo","actor":2,"pai":"?"},
                {"type":"dahai","actor":2,"pai":"1m","tsumogiri":true},
                {"type":"tsumo","actor":3,"pai":"?"},
                {"type":"dahai","actor":3,"pai":"2p","tsumogiri":true}
                ]"""
            )
        )
        == '{"type":"chi","actor":0,"target":3,"pai":"2p","consumed":["4p","3p"]}'  # noqa
    )
    assert player.tehai_tenhou == "12m134p4567s6z(p5z3)"

    assert (
        player.react(
            fmt(
                """[{"type":"chi","actor":0,"target":3,"pai":"2p","consumed":["4p","3p"]}]"""  # noqa
            )
        )
        == '{"type":"dahai","pai":"1p","actor":0,"tsumogiri":false}'
    )
    assert player.tehai_tenhou == "12m1p4567s6z(p5z3)(234p0)"
