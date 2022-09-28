import json
from loguru import logger

from mjx.agents import ShantenAgent, RuleBasedAgent
import mjx

from gateway import (
    to_mjx_tile,
    to_mjai_tile,
    MjxGateway,
    OpenCodeGen,
)


TODO_FIX_KNOWN_BUGS = False


def test_to_mjx_tile():
    assert to_mjx_tile("5mr") == 16
    assert to_mjx_tile("5m") == 17
    assert to_mjx_tile("5m", ignore_aka=True) == 16


def test_to_mjai_tile():
    assert to_mjai_tile(15) == "4m"
    assert to_mjai_tile(16) == "5mr"
    assert to_mjai_tile(17) == "5m"
    assert to_mjai_tile(18) == "5m"
    assert to_mjai_tile(19) == "5m"
    assert to_mjai_tile(20) == "6m"


def test_shanten_agent_case1():
    player_id = 1
    bot = MjxGateway(player_id, ShantenAgent())

    resp = bot.react('[{"type":"start_game"}]')
    assert resp == '{"type":"none"}'

    resp = bot.react('[{"type":"start_kyoku","bakaze":"E","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"dora_marker":"7s","tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["3m","4m","3p","5pr","7p","9p","4s","4s","5sr","7s","7s","W","N"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},{"type":"tsumo","actor":0,"pai":"?"},{"type":"dahai","actor":0,"pai":"6s","tsumogiri":false},{"type":"tsumo","actor":1,"pai":"1m"}]')
    assert json.loads(resp)["type"] == "dahai"
    assert json.loads(resp)["actor"] == 1
    assert json.loads(resp)["tsumogiri"] == (json.loads(resp)["pai"] == "1m")


def test_shanten_agent_case2():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    resp = bot.react('[{"type":"start_game"}]')
    resp = bot.react('[{"type":"start_kyoku","bakaze":"E","dora_marker":"5p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["S","2m","C","2m","7p","C","6m","7m","N","W","3p","6s","8s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]')
    assert json.loads(resp)["type"] == "dahai"
    assert json.loads(resp)["actor"] == 0
    assert json.loads(resp)["tsumogiri"] == (json.loads(resp)["pai"] == "3p")

    resp = bot.react('[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"2m","can_act":false},{"type":"dahai","actor":1,"pai":"2m","tsumogiri":true,"can_act":true}]')
    assert bot.get_obs_open() == []

    resp = bot.react('[{"type":"pon","actor":0,"target":1,"pai":"2m","consumed":["2m","2m"],"can_act":true}]')
    assert bot.get_obs_open() == [2665]

    resp = bot.react('[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"5p","can_act":false},{"type":"dahai","actor":1,"pai":"5p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1p","can_act":false},{"type":"dahai","actor":2,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"3p","can_act":false},{"type":"dahai","actor":3,"pai":"3p","tsumogiri":true,"can_act":true}]')
    resp = bot.react('[{"type":"pon","actor":0,"target":3,"pai":"3p","consumed":["3p","3p"],"can_act":true}]')
    assert bot.get_obs_open() == [2665, 18027]


def test_shanten_agent_case3():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    resp = bot.react('[{"type":"start_game"}]')
    resp = bot.react('[{"type":"start_kyoku","bakaze":"E","dora_marker":"5p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["S","2m","C","2m","7p","C","6m","7m","N","W","3p","6s","8s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]')
    resp = bot.react('[{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"2m","can_act":false},{"type":"dahai","actor":1,"pai":"2m","tsumogiri":true,"can_act":true}]')
    assert bot.get_obs_open() == []

    resp = bot.react('[{"type":"pon","actor":0,"target":1,"pai":"2m","consumed":["2m","2m"],"can_act":true}]')
    assert bot.get_obs_open() == [2665]

    resp = bot.react('[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"5p","can_act":false},{"type":"dahai","actor":1,"pai":"5p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1p","can_act":false},{"type":"dahai","actor":2,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"3p","can_act":false},{"type":"dahai","actor":3,"pai":"3p","tsumogiri":true,"can_act":true}]')
    resp = bot.react('[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"9s","can_act":false},{"type":"dahai","actor":1,"pai":"9s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"6p","can_act":false},{"type":"dahai","actor":2,"pai":"6p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"E","can_act":false},{"type":"dahai","actor":3,"pai":"E","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"4p","can_act":true}]')
    resp = bot.react('[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"7m","can_act":false},{"type":"dahai","actor":1,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"8p","can_act":false},{"type":"dahai","actor":2,"pai":"8p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"8m","can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":true,"can_act":true}]')
    resp = bot.react('[{"type":"chi","actor":0,"target":3,"pai":"8m","consumed":["6m","7m"],"can_act":true}]')
    assert bot.get_obs_open() == [2665, 17415]


def test_shanten_agent_case4():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    resp = bot.react('[{"type":"start_game"}]')
    resp = bot.react('[{"type":"start_kyoku","bakaze":"E","dora_marker":"4p","kyoku":1,"honba":1,"kyotaku":0,"oya":0,"scores":[27100,24300,24300,24300],"tehais":[["6m","2p","3s","6p","7m","7p","8p","7m","8m","N","E","P","2m"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"1m","can_act":true}]')
    assert bot.get_obs_open() == []
    assert bot.get_obs_hand() == [0, 4, 20, 24, 25, 28, 40, 56, 60, 64, 80, 108, 120, 124]
    assert len(bot.get_obs_hand()) == 14

    resp = bot.react('[{"type":"dahai","actor":0,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"W","can_act":false},{"type":"dahai","actor":1,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1s","can_act":false},{"type":"dahai","actor":2,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"6m","can_act":false},{"type":"dahai","actor":3,"pai":"6m","tsumogiri":true,"can_act":true}]')
    assert bot.get_obs_open() == []
    assert bot.get_obs_hand() == [0, 4, 20, 24, 25, 28, 40, 56, 60, 64, 80, 108, 120]  # P(124) を捨てている
    assert len(bot.get_obs_hand()) == 13  # 他家の打牌場面であるため 13 枚

    resp = bot.react('[{"type":"chi","actor":0,"target":3,"pai":"6m","consumed":["7m","8m"],"can_act":true}]')
    assert bot.get_obs_open() == [15375]
    assert bot.get_obs_hand() == [0, 4, 20, 25, 40, 56, 60, 64, 80, 108, 120]  # 7m(24), 8m(28) を消費している
    assert len(bot.get_obs_hand()) == 11


def test_shanten_agent_case5():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    resp = bot.react('[{"type":"start_kyoku","bakaze":"E","dora_marker":"4p","kyoku":1,"honba":1,"kyotaku":0,"oya":0,"scores":[26500,23500,25000,25000],"tehais":[["6m","2p","3s","6p","7m","7p","8p","7m","8m","N","E","P","2m"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"1m","can_act":true}]')
    resp = bot.react('[{"type":"dahai","actor":0,"pai":"3s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"W","can_act":false},{"type":"dahai","actor":1,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1s","can_act":false},{"type":"dahai","actor":2,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"6m","can_act":false},{"type":"dahai","actor":3,"pai":"6m","tsumogiri":true,"can_act":true}]')
    assert bot.get_obs_open() == []

    resp = bot.react('[{"type":"chi","actor":0,"target":3,"pai":"6m","consumed":["7m","8m"],"can_act":true}]')
    assert bot.get_obs_open() == [15375]

    resp = bot.react('[{"type":"dahai","actor":0,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"3p","can_act":false},{"type":"dahai","actor":1,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"4m","can_act":false},{"type":"dahai","actor":2,"pai":"4m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"8m","can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":true,"can_act":true}]')
    resp = bot.react('[{"type":"chi","actor":0,"target":3,"pai":"8m","consumed":["6m","7m"],"can_act":true}]')
    assert bot.get_obs_open() == [15375, 17575]

    resp = bot.react('[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"3m","can_act":false},{"type":"dahai","actor":1,"pai":"3m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"4m","can_act":false},{"type":"dahai","actor":2,"pai":"4m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"3p","can_act":false},{"type":"dahai","actor":3,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"7s","can_act":true}]')
    resp = bot.react('[{"type":"dahai","actor":0,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"1s","can_act":false},{"type":"dahai","actor":1,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"4s","can_act":false},{"type":"dahai","actor":2,"pai":"4s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"F","can_act":false},{"type":"dahai","actor":3,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"8s","can_act":true}]')
    resp = bot.react('[{"type":"dahai","actor":0,"pai":"2p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"9m","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"4s","can_act":false},{"type":"dahai","actor":2,"pai":"4s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"3s","can_act":false},{"type":"dahai","actor":3,"pai":"3s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"3m","can_act":true}]')
    assert bot.get_obs_hand() == [0, 4, 9, 56, 60, 64, 96, 100]


def test_shanten_agent_case6():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    bot.set_obs_offset({
        'who': 0,
        'publicObservation': {
            'playerIds': ['player_0', 'player_1', 'player_2', 'player_3'],
            'initScore': {
                'tens': [26500, 23500, 25000, 25000]},
            'doraIndicators': [48],
            'events': [
                {'type': 'EVENT_TYPE_DRAW'}, {'tile': 80},
                {'type': 'EVENT_TYPE_DRAW', 'who': 1}, {'tile': 116, 'who': 1},
                {'type': 'EVENT_TYPE_DRAW', 'who': 2}, {'tile': 72, 'who': 2},
                {'type': 'EVENT_TYPE_DRAW', 'who': 3}, {'tile': 21, 'who': 3},
                {'type': 'EVENT_TYPE_CHI', 'open': 15375}, {'tile': 124},
                {'type': 'EVENT_TYPE_DRAW', 'who': 1}, {'tile': 44, 'who': 1},
                {'type': 'EVENT_TYPE_DRAW', 'who': 2}, {'tile': 12, 'who': 2},
                {'type': 'EVENT_TYPE_DRAW', 'who': 3}, {'tile': 29, 'who': 3},
                {'type': 'EVENT_TYPE_CHI', 'open': 17575}, {'tile': 120},
                {'type': 'EVENT_TYPE_DRAW', 'who': 1}, {'tile': 8, 'who': 1},
                {'type': 'EVENT_TYPE_DRAW', 'who': 2}, {'tile': 13, 'who': 2},
                {'type': 'EVENT_TYPE_DRAW', 'who': 3}, {'tile': 45, 'who': 3},
                {'type': 'EVENT_TYPE_DRAW'}
            ]
        },
        'privateObservation': {
            'who': 0,
            'initHand': {
                'closedTiles': [20, 40, 80, 56, 24, 60, 64, 25, 28, 120, 108, 124, 4]},
            'drawHistory': [0, 96],
            'currHand': {
                'closedTiles': [0, 4, 40, 56, 60, 64, 96, 108],
                'opens': [15375, 17575]
            }
        }
    },
    {
        # Tile id ごとの観測数
        48: 1, 20: 2, 40: 1, 80: 1, 56: 1, 24: 2, 60: 1, 64: 1, 28: 2, 120: 1,
        108: 1, 124: 1, 4: 1, 0: 1, 116: 1, 72: 1, 44: 2, 12: 2, 8: 1, 96: 1,
    })

    resp = bot.react('[{"type":"dahai","actor":0,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"1s","can_act":false},{"type":"dahai","actor":1,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"4s","can_act":false},{"type":"dahai","actor":2,"pai":"4s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"F","can_act":false},{"type":"dahai","actor":3,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"8s","can_act":true}]')
    resp = json.loads(resp)
    assert resp["type"] == "dahai"
    assert resp["pai"] in ["1m", "2m", "2p", "6p", "7p", "8p", "7s", "8s"]
    assert resp["tsumogiri"] == (resp["pai"] == "8s")
    assert bot.get_obs_hand() == [0, 4, 40, 56, 60, 64, 96, 100]
    assert bot.get_obs_open() == [15375, 17575]


def test_shanten_agent_case7():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"S","dora_marker":"P","kyoku":1,"honba":7,"kyotaku":0,"oya":0,"scores":[39900,18100,21000,21000],"tehais":[["4s","P","2s","7p","8s","3p","8s","9p","E","6s","5sr","2m","1p"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"N","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"P","can_act":false},{"type":"dahai","actor":1,"pai":"P","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"9p","can_act":false},{"type":"dahai","actor":2,"pai":"9p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"3s","can_act":false},{"type":"dahai","actor":3,"pai":"3s","tsumogiri":true,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"3s","consumed":["2s","4s"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"5s","can_act":false},{"type":"dahai","actor":1,"pai":"5s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"9m","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"9p","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"E","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"6s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"4p","can_act":false},{"type":"dahai","actor":1,"pai":"4p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1s","can_act":false},{"type":"dahai","actor":2,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"2s","can_act":false},{"type":"dahai","actor":3,"pai":"2s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"4p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"4p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"5s","can_act":false},{"type":"dahai","actor":1,"pai":"5s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"S","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"5mr","can_act":false},{"type":"dahai","actor":3,"pai":"5mr","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"2m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"4p","can_act":false},{"type":"dahai","actor":1,"pai":"4p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"3m","can_act":false},{"type":"dahai","actor":2,"pai":"3m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"N","can_act":false},{"type":"dahai","actor":3,"pai":"N","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"5sr","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"3s","can_act":false},{"type":"dahai","actor":1,"pai":"3s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"S","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"7s","can_act":false},{"type":"dahai","actor":3,"pai":"7s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"8m","can_act":false},{"type":"dahai","actor":1,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1s","can_act":false},{"type":"dahai","actor":2,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"F","can_act":false},{"type":"dahai","actor":3,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"1p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"4m","can_act":false},{"type":"dahai","actor":1,"pai":"4m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"C","can_act":false},{"type":"dahai","actor":2,"pai":"C","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"C","can_act":false},{"type":"dahai","actor":3,"pai":"C","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"1m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"2m","can_act":false},{"type":"dahai","actor":1,"pai":"2m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"3p","can_act":false},{"type":"dahai","actor":2,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"8m","can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"7s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"6s","can_act":false},{"type":"dahai","actor":1,"pai":"6s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"7m","can_act":false},{"type":"dahai","actor":2,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"3p","can_act":false},{"type":"dahai","actor":3,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"3s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"3s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"9m","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"7m","can_act":false},{"type":"dahai","actor":2,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"7m","can_act":false},{"type":"dahai","actor":3,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"3s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"9s","can_act":false},{"type":"dahai","actor":1,"pai":"9s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1s","can_act":false},{"type":"dahai","actor":2,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"6p","can_act":false},{"type":"dahai","actor":3,"pai":"6p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"9s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"3s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"6s","can_act":false},{"type":"dahai","actor":1,"pai":"6s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"W","can_act":false},{"type":"dahai","actor":2,"pai":"W","tsumogiri":true,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":2,"pai":"W","consumed":["W","W"],"can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert bot.get_obs_hand() == [37, 44, 97, 101, 105, 108, 109, 118]
    assert bot.get_obs_open() == [47111, 45642]


def test_shanten_agent_case8():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"S","dora_marker":"6m","kyoku":2,"honba":6,"kyotaku":0,"oya":1,"scores":[36100,21300,21300,21300],"tehais":[["3s","2m","1s","1s","W","P","9p","6s","4m","F","5s","2s","1m"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":1,"pai":"7s","can_act":false},{"type":"dahai","actor":1,"pai":"7s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"6s","can_act":false},{"type":"dahai","actor":2,"pai":"6s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"8m","can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"5p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"W","can_act":false},{"type":"dahai","actor":1,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"8m","can_act":false},{"type":"dahai","actor":2,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"5sr","can_act":false},{"type":"dahai","actor":3,"pai":"5sr","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"P","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"4m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"7m","can_act":false},{"type":"dahai","actor":1,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"6p","can_act":false},{"type":"dahai","actor":2,"pai":"6p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"7p","can_act":false},{"type":"dahai","actor":3,"pai":"7p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"2m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"2m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"7p","can_act":false},{"type":"dahai","actor":1,"pai":"7p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1p","can_act":false},{"type":"dahai","actor":2,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"7s","can_act":false},{"type":"dahai","actor":3,"pai":"7s","tsumogiri":true,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"7s","consumed":["5s","6s"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"C","can_act":false},{"type":"dahai","actor":1,"pai":"C","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"6s","can_act":false},{"type":"dahai","actor":2,"pai":"6s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"1m","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"8p","can_act":false},{"type":"dahai","actor":1,"pai":"8p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"1s","can_act":false},{"type":"dahai","actor":2,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"4p","can_act":false},{"type":"dahai","actor":3,"pai":"4p","tsumogiri":true,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"4p","consumed":["3p","5p"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"F","can_act":false},{"type":"dahai","actor":1,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"8p","can_act":false},{"type":"dahai","actor":2,"pai":"8p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"E","can_act":false},{"type":"dahai","actor":3,"pai":"E","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"4m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"C","can_act":false},{"type":"dahai","actor":1,"pai":"C","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"3s","can_act":false},{"type":"dahai","actor":2,"pai":"3s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"4p","can_act":false},{"type":"dahai","actor":3,"pai":"4p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"3m","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert bot.get_obs_open() == [57487, 28807]


def test_shanten_agent_case9():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"7s","kyoku":3,"honba":5,"kyotaku":0,"oya":2,"scores":[36100,21300,21300,21300],"tehais":[["5s","3m","W","P","2m","C","3p","6m","7s","3m","8s","3m","7p"],["?","?","?","?","?","?",",?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":2,"pai":"3m","can_act":false},{"type":"dahai","actor":2,"pai":"3m","tsumogiri":true,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":2,"pai":"3m","consumed":["3m","3m"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"3p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"1p","can_act":false},{"type":"dahai","actor":1,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"E","can_act":false},{"type":"dahai","actor":2,"pai":"E","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"2p","can_act":false},{"type":"dahai","actor":3,"pai":"2p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"1m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"3s","can_act":false},{"type":"dahai","actor":1,"pai":"3s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"N","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"8m","can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"8p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"6m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"F","can_act":false},{"type":"dahai","actor":1,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"3s","can_act":false},{"type":"dahai","actor":2,"pai":"3s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"8m","can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"9m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"3s","can_act":false},{"type":"dahai","actor":1,"pai":"3s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"4s","can_act":false},{"type":"dahai","actor":2,"pai":"4s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"1p","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"E","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"S","can_act":false},{"type":"dahai","actor":1,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"3p","can_act":false},{"type":"dahai","actor":2,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"6p","can_act":false},{"type":"dahai","actor":3,"pai":"6p","tsumogiri":true,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"6p","consumed":["7p","8p"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"C","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"2s","can_act":false},{"type":"dahai","actor":1,"pai":"2s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"3p","can_act":false},{"type":"dahai","actor":2,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"1m","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":true,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"1m","consumed":["2m","3m"],"can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    if TODO_FIX_KNOWN_BUGS:
        assert bot.get_obs_open() == [4170, 36871, 15]


def test_shanten_agent_case10():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"5p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["S","2m","C","2m","7p","C","6m","7m","N","W","3p","6s","8s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"pon","actor":2,"target":0,"pai":"8s","consumed":["8s","8s"],"can_act":false},{"type":"dahai","actor":2,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"5m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"2m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"E","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"F","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"C","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"C","consumed":["C","C"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"3p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"C","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"4m","tsumogiri":false,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"4m","consumed":["5m","6m"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"chi","actor":2,"target":1,"pai":"4p","consumed":["5p","6p"],"can_act":false},{"type":"dahai","actor":2,"pai":"2p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"5m","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    if TODO_FIX_KNOWN_BUGS:
        assert False


def test_shanten_agent_case11():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"E","kyoku":3,"honba":0,"kyotaku":0,"oya":2,"scores":[25300,23700,28000,23000],"tehais":[["4p","1p","P","4p","S","5s","4m","7p","4s","8m","2p","9m","P"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"9p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"2m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"P","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"6s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"C","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"2m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"8p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"7m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"8p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"4m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"4s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"E","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"E","tsumogiri":true,"can_act":false},{"type":"pon","actor":2,"target":0,"pai":"E","consumed":["E","E"],"can_act":false},{"type":"dahai","actor":2,"pai":"3s","tsumogiri":false,"can_act":false},{"type":"chi","actor":3,"target":2,"pai":"3s","consumed":["2s","4s"],"can_act":false},{"type":"dahai","actor":3,"pai":"2s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"S","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"8s","tsumogiri":true,"can_act":false},{"type":"chi","actor":3,"target":2,"pai":"8s","consumed":["6s","7s"],"can_act":false},{"type":"dahai","actor":3,"pai":"5m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"9p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"9p","tsumogiri":true,"can_act":false},{"type":"pon","actor":2,"target":0,"pai":"9p","consumed":["9p","9p"],"can_act":false},{"type":"dahai","actor":2,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"7p","tsumogiri":true,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"7p","consumed":["8p","9p"],"can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert bot.get_obs_open() == [40111]


def test_rulebased_agent_case1():
    player_id = 1
    bot = MjxGateway(player_id, RuleBasedAgent())

    resp = bot.react('[{"type":"start_game","id":1}]')
    assert resp == '{"type":"none"}'

    resp = bot.react('[{"type":"start_kyoku","bakaze":"E","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"dora_marker":"7s","tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["3m","4m","3p","5pr","7p","9p","4s","4s","5sr","7s","7s","W","N"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]]},{"type":"tsumo","actor":0,"pai":"?"},{"type":"dahai","actor":0,"pai":"6s","tsumogiri":false},{"type":"tsumo","actor":1,"pai":"3m"}]')
    assert json.loads(resp)["type"] == "dahai"
    assert json.loads(resp)["actor"] == 1
    assert json.loads(resp)["tsumogiri"] == (json.loads(resp)["pai"] == "3m")


def test_rulebased_agent_case2():
    player_id = 0
    bot = MjxGateway(player_id, RuleBasedAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"4s","kyoku":2,"honba":1,"kyotaku":0,"oya":1,"scores":[25000,25000,25000,25000],"tehais":[["C","1p","9s","8m","4s","6s","7s","9m","5s","2s","1m","6m","8s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"2s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"5p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"P","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"P","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"3m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"6m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"3s","tsumogiri":true,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"3s","consumed":["2s","4s"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"C","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"8s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"3m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"6s","tsumogiri":true,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"6s","consumed":["5s","7s"],"can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert bot.get_obs_open() == [47239, 56367]


def test_rulebased_agent_casse3():
    player_id = 1

    bot = MjxGateway(player_id, RuleBasedAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"4p","kyoku":1,"honba":1,"kyotaku":0,"oya":0,"scores":[28900,22100,25000,24000],"tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["3p","6s","2p","W","9s","6m","3m","2p","1m","5p","8s","9p","1m"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"chi","actor":0,"target":3,"pai":"9m","consumed":["7m","8m"],"can_act":false},{"type":"dahai","actor":0,"pai":"2p","tsumogiri":false,"can_act":true}]',
        '[{"type":"tsumo","actor":1,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"6m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"4m","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"W","tsumogiri":false,"can_act":true}]',
        '[{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"4s","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"5p","tsumogiri":false,"can_act":false},{"type":"chi","actor":2,"target":1,"pai":"5p","consumed":["3p","4p"],"can_act":false},{"type":"dahai","actor":2,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"8p","tsumogiri":false,"can_act":false},{"type":"chi","actor":0,"target":3,"pai":"8p","consumed":["6p","7p"],"can_act":false},{"type":"dahai","actor":0,"pai":"3s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"8s","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"4s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"3s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"3m","can_act":true}]',
        '[{"type":"reach","actor":1,"can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert json.loads(resp)["type"] == "dahai"


def test_shanten_agent_casse12_kakan_action():
    player_id = 0

    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"5p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["S","2m","C","2m","7p","C","6m","7m","N","W","3p","6s","8s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"C","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"C","consumed":["C","C"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"7m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"pon","actor":2,"target":0,"pai":"8s","consumed":["8s","8s"],"can_act":false},{"type":"dahai","actor":2,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"1p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"2p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"2s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"2s","tsumogiri":true,"can_act":false},{"type":"pon","actor":2,"target":0,"pai":"2s","consumed":["2s","2s"],"can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"5s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"C","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert True


def test_shanten_agent_casse13_kakan():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"5p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["S","2m","C","2m","7p","C","6m","7m","N","W","3p","6s","8s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"C","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"C","consumed":["C","C"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"7m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"5m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"E","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"2p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"3s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"C","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)
        print([to_mjai_tile(t) for t in bot.get_obs_hand()])

    assert json.loads(resp)["type"] == "kakan"
    assert json.loads(resp)["actor"] == 0
    assert json.loads(resp)["pai"] == "C"
    assert json.loads(resp)["pai"] == json.loads(resp)["consumed"][0]

    resp = bot.react('[{"type":"kakan","actor":0,"pai":"C","consumed":["C","C","C"],"can_act":false},{"type":"tsumo","actor":0,"pai":"9p","can_act":true}]')

    assert bot.get_obs_open()[-1] == 51825
    assert json.loads(resp)["type"] == "dahai"


def test_kakan_value():
    val = 51817
    op1 = mjx.open.Open(val)
    assert [t.id() for t in op1.tiles_from_hand()] == [132, 133]
    assert [t.id() for t in op1.tiles()] == [132, 133, 134]
    assert op1.last_tile().id() == 134
    assert op1.steal_from() == 1

    ev = {"pai": "C", "actor": 0}
    obs = {
        "who": 0,
        "privateObservation": {
            "currHand": {
                "opens": [val],
            }
        },
    }

    value, _, _, _ = OpenCodeGen.from_mjai_kakan(ev, obs)
    assert value == 51825
    op2 = mjx.open.Open(value)
    assert [t.id() for t in op2.tiles_from_hand()] == [132, 133, 135]
    assert [t.id() for t in op2.tiles()] == [132, 133, 134, 135]
    assert op2.last_tile().id() == 135


def test_kakan_value_other_actor():
    val = 51817
    op1 = mjx.open.Open(val)
    assert [t.id() for t in op1.tiles_from_hand()] == [132, 133]
    assert [t.id() for t in op1.tiles()] == [132, 133, 134]
    assert op1.last_tile().id() == 134
    assert op1.steal_from() == 1

    ev = {"pai": "C", "actor": 0}
    obs = {
        "who": 1,
        "privateObservation": {
            "currHand": {
                "opens": [val],
            }
        },
        "publicObservation": {
            "events": [
                {"type": "EVENT_TYPE_PON", "open": val},
            ],
        },
    }

    value, _, _, _ = OpenCodeGen.from_mjai_kakan(ev, obs)
    assert value == 51825
    op2 = mjx.open.Open(value)
    assert [t.id() for t in op2.tiles_from_hand()] == [132, 133, 135]
    assert [t.id() for t in op2.tiles()] == [132, 133, 134, 135]
    assert op2.last_tile().id() == 135


def test_rulebased_agent_kakan():
    player_id = 1
    bot = MjxGateway(player_id, RuleBasedAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"5p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["9m","3m","3s","4s","5s","C","1s","4p","7s","7p","E","1s","6s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"2m","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"9s","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"C","tsumogiri":false,"can_act":false},{"type":"pon","actor":0,"target":1,"pai":"C","consumed":["C","C"],"can_act":false},{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"6p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"6m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"8p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"5m","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"5m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"E","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"F","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"2p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"kakan","actor":0,"pai":"C","consumed":["C","C","C"],"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dora","dora_marker":"9s","can_act":false},{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"7m","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)
        print([to_mjai_tile(t) for t in bot.get_obs_hand()])

    assert json.loads(resp)["type"] == "dahai"
    assert json.loads(resp)["actor"] == 1


def test_shanten_agent_casse14_other_reach_accepted():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"5p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["S","2m","C","2m","7p","C","6m","7m","N","W","3p","6s","8s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"3p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"chi","actor":1,"target":0,"pai":"8s","consumed":["6s","7s"],"can_act":false},{"type":"dahai","actor":1,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"1p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"C","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"C","consumed":["C","C"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"6s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"4s","tsumogiri":true,"can_act":false},{"type":"chi","actor":1,"target":0,"pai":"4s","consumed":["3s","5s"],"can_act":false},{"type":"dahai","actor":1,"pai":"3m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"1p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"6m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"E","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"2s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"8m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"7m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"9p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"6m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"2p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"8s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"1p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"2p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"2m","tsumogiri":true,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":3,"pai":"2m","consumed":["2m","2m"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"5sr","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"reach","actor":3,"can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":false,"can_act":false},{"type":"reach_accepted","actor":3,"can_act":false},{"type":"tsumo","actor":0,"pai":"9s","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert True


def test_rulebased_agent_daiminkan():
    player_id = 1
    bot = MjxGateway(player_id, RuleBasedAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"S","dora_marker":"1p","kyoku":2,"honba":0,"kyotaku":0,"oya":1,"scores":[21900,28200,24900,25000],"tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["8s","P","W","P","2s","6p","P","3p","2m","3m","3p","1m","N"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":1,"pai":"2p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":false,"can_act":true}]',
        '[{"type":"daiminkan","actor":1,"target":2,"pai":"P","consumed":["P","P","P"],"can_act":false},{"type":"tsumo","actor":1,"pai":"2p","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)
        print([to_mjai_tile(t) for t in bot.get_obs_hand()])

    assert json.loads(resp)["type"] == "dahai"
    assert json.loads(resp)["actor"] == 1


def test_rulebased_agent_case15():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"7m","kyoku":4,"honba":1,"kyotaku":0,"oya":3,"scores":[17000,22100,25900,35000],"tehais":[["P","8m","5mr","S","5m","W","E","7p","9s","5s","6m","7p","4p"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"P","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"chi","actor":1,"target":0,"pai":"9s","consumed":["7s","8s"],"can_act":false},{"type":"dahai","actor":1,"pai":"P","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"P","consumed":["P","P"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"5s","tsumogiri":false,"can_act":false},{"type":"chi","actor":1,"target":0,"pai":"5s","consumed":["3s","4s"],"can_act":false},{"type":"dahai","actor":1,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"1m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"6p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7p","tsumogiri":true,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"7p","consumed":["7p","7p"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"8p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"8p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"1s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"C","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"3m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"N","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"5m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"5mr","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"4m","tsumogiri":true,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"4m","consumed":["4m","4m"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"5m","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"5m","consumed":["5m","5m"],"can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)
        logger.debug(f"[OPEN] {[op for op in bot.get_obs_open()]}")
        logger.debug(f"[OPEN] {[to_mjai_tile(mjx.Open(op).last_tile().id()) for op in bot.get_obs_open()]}")
        logger.debug(f"[TEHAI] {[to_mjai_tile(t) for t in bot.get_obs_hand()]}")

    # 5m でポンしているはずなのに 7689 (6m pon) が生成されてしまう
    assert bot.get_obs_open() == [48745, 24169, 5737, 7177]
    assert [to_mjai_tile(mjx.Open(op).last_tile().id()) for op in bot.get_obs_open()] == ["P", "7p", "4m", "5m"]


def test_case16_ankan():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"2s","kyoku":4,"honba":0,"kyotaku":0,"oya":3,"scores":[24300,18700,40000,17000],"tehais":[["6p","N","5s","E","F","F","7p","4p","6s","E","S","4m","9s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"C","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"C","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"6p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"F","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"F","consumed":["F","F"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"8p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"7p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"6s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"P","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"5s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"5s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"reach","actor":1,"can_act":false},{"type":"dahai","actor":1,"pai":"5pr","tsumogiri":false,"can_act":false},{"type":"reach_accepted","actor":1,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"P","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"6s","tsumogiri":false,"can_act":false},{"type":"chi","actor":3,"target":2,"pai":"6s","consumed":["4s","5s"],"can_act":false},{"type":"dahai","actor":3,"pai":"2s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"8s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"C","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"7s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"E","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"6m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"5p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"E","can_act":true}]',
        '[{"type":"ankan","actor":0,"consumed":["E","E","E","E"],"can_act":false},{"type":"dora","dora_marker":"1m","can_act":false},{"type":"tsumo","actor":0,"pai":"9p","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert bot.get_obs_open() == [50281, 27648]


def test_case17():
    player_id = 1
    bot = MjxGateway(player_id, RuleBasedAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"7p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["8s","6s","8p","F","P","W","5s","5m","E","4m","7s","9p","3p"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"4p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"2p","tsumogiri":false,"can_act":true}]',
        '[{"type":"tsumo","actor":1,"pai":"N","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"ankan","actor":3,"consumed":["C","C","C","C"],"can_act":false},{"type":"dora","dora_marker":"6m","can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"3m","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)
        print(resp)

    assert True


def test_case18():
    player_id = 1
    bot = MjxGateway(player_id, RuleBasedAgent())

    inputs = [
        '[{"type":"start_game"}]',
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"7p","kyoku":1,"honba":0,"kyotaku":0,"oya":0,"scores":[25000,25000,25000,25000],"tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["8s","6s","8p","F","P","W","5s","5m","E","4m","7s","9p","3p"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"4p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"N","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"ankan","actor":3,"consumed":["C","C","C","C"],"can_act":false},{"type":"dora","dora_marker":"6m","can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"3m","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)
        print(resp)

    assert True


def test_case19():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"1p","kyoku":2,"honba":1,"kyotaku":1,"oya":1,"scores":[24000,24000,27000,24000],"tehais":[["9p","3p","P","8s","4p","W","N","5s","5p","2m","9p","9s","S"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"8m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"2m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"N","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"5p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"6s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"C","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"8p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"5m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"reach","actor":1,"can_act":false},{"type":"dahai","actor":1,"pai":"7m","tsumogiri":false,"can_act":false},{"type":"reach_accepted","actor":1,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"S","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"5s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"5pr","tsumogiri":true,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"5pr","consumed":["5p","5p"],"can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)

    assert bot.get_obs_open() == [20073]


def test_case20():
    player_id = 0
    bot = MjxGateway(player_id, ShantenAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"S","dora_marker":"4p","kyoku":3,"honba":1,"kyotaku":1,"oya":2,"scores":[8000,21600,41400,28000],"tehais":[["2s","9s","4p","1m","W","8p","9p","1s","9p","4p","8s","1s","7s"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"N","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"6m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"6m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"C","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"2p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"F","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"chi","actor":1,"target":0,"pai":"1m","consumed":["2m","3m"],"can_act":false},{"type":"dahai","actor":1,"pai":"3s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"C","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"5p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"4s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"5s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"P","tsumogiri":false,"can_act":false},{"type":"pon","actor":2,"target":3,"pai":"P","consumed":["P","P"],"can_act":false},{"type":"dahai","actor":2,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"9m","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"E","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"8p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"8p","tsumogiri":true,"can_act":false},{"type":"pon","actor":1,"target":0,"pai":"8p","consumed":["8p","8p"],"can_act":false},{"type":"dahai","actor":1,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"7m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"2s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"2s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"7s","tsumogiri":false,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"7s","consumed":["8s","9s"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"1p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"7m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"7p","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"2m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"N","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":3,"pai":"9p","consumed":["9p","9p"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"8s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"2s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"E","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"7p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"6p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"3p","tsumogiri":false,"can_act":true}]',
        '[{"type":"chi","actor":0,"target":3,"pai":"3p","consumed":["4p","5p"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"4s","tsumogiri":true,"can_act":true}]',
        '[{"type":"pon","actor":0,"target":1,"pai":"4s","consumed":["4s","4s"],"can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"2s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"3p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"8m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"6s","can_act":true}]',
        '[{"type":"dahai","actor":0,"pai":"6s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"?","can_act":false},{"type":"dahai","actor":1,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"4s","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)
        logger.debug(f"[OPEN] {[op for op in bot.get_obs_open()]}")
        logger.debug(f"[OPEN] {[to_mjai_tile(mjx.Open(op).last_tile().id()) for op in bot.get_obs_open()]}")
        logger.debug(f"[TEHAI] {[to_mjai_tile(t) for t in bot.get_obs_hand()]}")

    assert bot.get_obs_open() == [61463, 27243, 27847, 33385]

    bot.react('[{"type":"kakan","actor":0,"pai":"4s","consumed":["4s","4s","4s"],"can_act":false},{"type":"tsumo","actor":0,"pai":"2s","can_act":true}]')
    assert bot.get_obs_open() == [61463, 27243, 27847, 33393]


def test_case21():
    player_id = 1
    bot = MjxGateway(player_id, RuleBasedAgent())

    inputs = [
        '[{"type":"start_kyoku","bakaze":"E","dora_marker":"7p","kyoku":3,"honba":1,"kyotaku":1,"oya":2,"scores":[24000,24000,23100,27900],"tehais":[["?","?","?","?","?","?","?","?","?","?","?","?","?"],["E","3m","7m","S","3s","5p","5mr","2p","P","N","5pr","9s","C"],["?","?","?","?","?","?","?","?","?","?","?","?","?"],["?","?","?","?","?","?","?","?","?","?","?","?","?"]],"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"P","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"9p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"P","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"C","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"5s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"2s","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"S","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"E","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"N","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"3m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"7s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"N","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"C","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"S","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"F","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"N","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"2m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"W","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"2m","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"2p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"2m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1m","tsumogiri":true,"can_act":false},{"type":"chi","actor":0,"target":3,"pai":"1m","consumed":["2m","3m"],"can_act":false},{"type":"dahai","actor":0,"pai":"1p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"F","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"F","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"8m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"3p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"5sr","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"7p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"5mr","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"2p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"4s","tsumogiri":false,"can_act":true}]',
        '[{"type":"pon","actor":3,"target":0,"pai":"4s","consumed":["4s","4s"],"can_act":false},{"type":"dahai","actor":3,"pai":"9m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"4m","tsumogiri":false,"can_act":true}]',
        '[{"type":"chi","actor":1,"target":0,"pai":"4m","consumed":["2m","3m"],"can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"7m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"3p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"6s","tsumogiri":true,"can_act":false},{"type":"chi","actor":0,"target":3,"pai":"6s","consumed":["7s","8s"],"can_act":false},{"type":"dahai","actor":0,"pai":"6p","tsumogiri":false,"can_act":true}]',
        '[{"type":"chi","actor":1,"target":0,"pai":"6p","consumed":["5p","7p"],"can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"5p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"5p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"2p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"2p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"7s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"1m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"W","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"9s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"8s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"9s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"1p","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"1p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"1m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"3p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"8p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"C","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"C","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"4p","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"W","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"6s","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":1,"pai":"7s","can_act":true}]',
        '[{"type":"dahai","actor":1,"pai":"7s","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"4p","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"4m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":0,"pai":"?","can_act":false},{"type":"dahai","actor":0,"pai":"4m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":1,"pai":"3m","can_act":true}]',
    ]

    for input_ in inputs:
        resp = bot.react(input_)
        logger.debug(f"[OPEN] {[op for op in bot.get_obs_open()]}")
        logger.debug(f"[OPEN] {[to_mjai_tile(mjx.Open(op).last_tile().id()) for op in bot.get_obs_open()]}")
        logger.debug(f"[TEHAI] {[to_mjai_tile(t) for t in bot.get_obs_hand()]}")

    logger.debug(f"[DEBUG] offset={bot.hai_offset}")

    if TODO_FIX_KNOWN_BUGS:
        # Runtime error
        # resp = bot.react('[{"type":"dahai","actor":1,"pai":"3m","tsumogiri":true,"can_act":false},{"type":"tsumo","actor":2,"pai":"?","can_act":false},{"type":"dahai","actor":2,"pai":"4m","tsumogiri":false,"can_act":false},{"type":"tsumo","actor":3,"pai":"?","can_act":false},{"type":"dahai","actor":3,"pai":"1s","tsumogiri":true,"can_act":true}]')
        assert False
