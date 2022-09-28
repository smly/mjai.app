import json
import sys

from mjx import Observation
from mjx.agents import ShantenAgent
from gateway import MjxGateway, to_mjai_tile


def main():
    player_id = int(sys.argv[1])
    assert player_id in range(4)
    bot = MjxGateway(player_id, ShantenAgent())

    while True:
        line = sys.stdin.readline().strip()
        resp = bot.react(line)
        sys.stdout.write(resp + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
