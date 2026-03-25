from game_executables import GameExecutables


class GameStateOverride(GameExecutables):
    """
    Overrides and extends universal state.py functions with game-specific behaviour.
    """

    def reset_book(self) -> None:
        super().reset_book()
        self.tumble_win = 0
        self.x_tile_position = None
        self.x_tile_cluster_hit = False
        # SUPER_BONUS base game uses super_basegame_type so freespin_triggers
        # resolves to {4:10, 5:11, 6:12, 7:13} instead of the base {3:8}.
        if getattr(self, "betmode", None) == "super_bonus":
            self.gametype = self.config.super_basegame_type

    def reset_fs_spin(self) -> None:
        super().reset_fs_spin()
        self.x_tile_position = None
        self.x_tile_cluster_hit = False

    def assign_special_sym_function(self) -> None:
        pass

    def check_repeat(self) -> None:
        """Checks if the spin failed any criteria constraint."""
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            conditions = self.get_current_distribution_conditions()

            if conditions["force_freegame"] and not self.triggered_freegame:
                self.repeat = True

            # feature_cluster_drop: spin must produce at least one cluster win
            if conditions.get("force_cluster") and self.win_manager.running_bet_win == 0:
                self.repeat = True

            # feature_max_multi_tile: a winning cluster must have landed on the X-Tile
            if conditions.get("force_x_tile_cluster") and not self.x_tile_cluster_hit:
                self.repeat = True

            if self.win_manager.running_bet_win == 0 and self.criteria != "0":
                self.repeat = True
