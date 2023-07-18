import importlib
import json
import sys


def test_get_best_tile():
    tiles = [
        "E",
        "6p",
        "9m",
        "8m",
        "C",
        "2s",
        "7m",
        "S",
        "6m",
        "1m",
        "S",
        "3s",
        "8m",
        "1m",
    ]
    sys.path.append("./players/shanten")
    mod = importlib.import_module("bot")
    best_choice = mod.get_best_tile(tiles)
    assert best_choice in ["6p", "C", "E"]


def test_shanten_bot():
    sys.path.append("./players/shanten")
    mod = importlib.import_module("bot")

    player_id = 0
    bot = mod.Bot(player_id)
    resp = bot.react('[{"type":"start_game","id":' + str(player_id) + "}]")
    assert resp == '{"type":"none"}'

    resp = bot.react(
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"2s","kyoku":1,"honba":0,'  # noqa: E501
        '"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],'
        '"tehais":[["E","6p","9m","8m","C","2s","7m","S","6m","1m","S","3s","8m"],'  # noqa: E501
        '["?","?","?","?","?","?","?","?","?","?","?","?","?"],'
        '["?","?","?","?","?","?","?","?","?","?","?","?","?"],'
        '["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},'
        '{"type":"tsumo","actor":0,"pai":"1m"}]'
    )
    resp_json = json.loads(resp)
    assert resp_json["pai"] in ["6p", "C", "E"]

    player_id = 1
    bot = mod.Bot(player_id)
    resp = bot.react('[{"type": "start_game","id":' + str(player_id) + "}]")
    assert resp == '{"type":"none"}'

    resp = bot.react(
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"2s","kyoku":1,"honba":0,'  # noqa: E501
        '"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],'
        '"tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],'
        '["5pr","2p","1p","C","3p","9p","9m","7s","2p","8s","3p","3m","3p"],'
        '["?","?","?","?","?","?","?","?","?","?","?","?","?"],'
        '["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},'
        '{"type":"tsumo","actor":0,"pai":"?"},'
        '{"type":"dahai","actor":0,"pai":"1m","tsumogiri":true},'
        '{"type":"tsumo","actor":1,"pai":"2s"}]'
    )
    resp_json = json.loads(resp)
    assert resp_json["pai"] == "2s"
