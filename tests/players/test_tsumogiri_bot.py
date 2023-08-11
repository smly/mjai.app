import importlib
import sys


def test_tsumobiri_bot():
    sys.path.append("./examples/tsumogiri")
    mod = importlib.import_module("bot")

    for player_id in range(4):
        bot = mod.Bot(player_id)
        resp = bot.react(
            '[{"type": "start_game","id":' + str(player_id) + "}]"
        )
        assert resp == '{"type":"none"}'
