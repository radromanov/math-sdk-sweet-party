from game_override import GameStateOverride
from game_events import spawn_x_tile_event


class GameState(GameStateOverride):
    """Core function handling simulation results."""

    def _win_gametype(self) -> str:
        """Resolve gametype for win tracking. super_basegame_type is a base game phase."""
        if self.gametype == self.config.super_basegame_type:
            return self.config.basegame_type
        return self.gametype

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()
            self.draw_board()
            self.assign_symbol_multipliers()
            self.spawn_x_tile()
            spawn_x_tile_event(self)

            self.get_clusters_update_wins()
            self.emit_tumble_win_events()

            while self.win_data["totalWin"] > 0 and not self.wincap_triggered:
                self.tumble_game_board()
                self.assign_symbol_multipliers()  # assign to newly revealed symbols
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self._win_gametype())

            if self.check_fs_condition() and self.check_freespin_entry():
                self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.spawn_x_tile()
            spawn_x_tile_event(self)
            self.draw_board()
            self.assign_symbol_multipliers()

            self.get_clusters_update_wins()
            self.emit_tumble_win_events()

            while self.win_data["totalWin"] > 0 and not self.wincap_triggered:
                self.tumble_game_board()
                self.assign_symbol_multipliers()  # assign to newly revealed symbols
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
