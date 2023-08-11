"""Reference implementtation with using high-level API.
"""
from mjai import Bot


class RulebaseBot(Bot):
    # RiichiBot + yakuhai pon + {chi,pon} if yaku is ready.
    # {chi,pon} if tanyao. no call if tenpai.
    # scoring discard tiles with ukeire, imp candidate and number (19,28,?z)
    pass
