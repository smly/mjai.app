"""Reference implementtation with using high-level API.
"""
from mjai import Bot


class RulebaseBot(Bot):
    def think(self) -> str:
        if self.can_tsumo_agari:
            return self.action_tsumo_agari()
        elif self.can_ron_agari:
            return self.action_ron_agari()
        elif self.can_riichi:
            return self.action_riichi()

        if self.can_pon and self.is_yakuhai(self.last_kawa_tile):
            # TODO: 手の進まないポンはしない
            return self.action_pon(consumed=[self.last_kawa_tile] * 2)

        elif self.can_chi and len(self.get_call_events(self.player_id)) > 0:
            # TODO: 手の進まないポンはしない
            # TODO: chi においてドラを考慮する
            # TODO: 候補を tools から取得して選択できるようにする
            # TODO: 候補に対して hand analysis して受け入れ枚数最大となるようなチーを選択する

            color = self.last_kawa_tile[1]
            target_num = int(self.last_kawa_tile[0])
            if self.can_chi_high:
                consumed = [
                    f"{target_num - 2}{color}",
                    f"{target_num - 1}{color}",
                ]
                return self.action_chi(consumed=consumed)
            elif self.can_chi_low:
                consumed = [
                    f"{target_num + 2}{color}",
                    f"{target_num + 1}{color}",
                ]
                return self.action_chi(consumed=consumed)
            else:
                consumed = [
                    f"{target_num - 1}{color}",
                    f"{target_num + 1}{color}",
                ]
                return self.action_chi(consumed=consumed)

        if self.can_discard:
            # TODO: 喰いタン判定
            # TODO: 受け入れ枚数最大となるような捨牌を選択
            candidates = self.find_improving_tiles()
            for discard_tile, improving_tiles in candidates:
                return self.action_discard(discard_tile)

            return self.action_discard(
                self.last_self_tsumo or self.tehai_mjai[0]
            )
        else:
            # Response toward start_game, ryukyoku, etc
            return self.action_nothing()
