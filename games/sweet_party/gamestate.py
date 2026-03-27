from game_override import GameStateOverride
from src.events.events import fs_trigger_event


class GameState(GameStateOverride):
    """Core function handling simulation results."""

    def run_spin(self, sim, simulation_seed=None):
        self.reset_seed(sim)
        self.repeat = True
        while self.repeat:
            self.reset_book()

            if self.get_current_betmode().get_buybonus():
                # Buy bonus: skip base game, go straight to 8 free spins
                self.triggered_freegame = True
                self.tot_fs = 8
                self.refresh_special_syms()
                self.record({"kind": 3, "symbol": "scatter", "gametype": self.config.basegame_type})
                fs_trigger_event(self, basegame_trigger=True, freegame_trigger=False)
                self.run_freespin()
            else:
                # Normal flow: base game spin
                self.draw_board()
                self.maybe_spawn_xtile()

                self.get_clusters_update_wins()
                self.emit_tumble_win_events()

                while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                    self.tumble_game_board()
                    self.get_clusters_update_wins()
                    self.emit_tumble_win_events()

                self.set_end_tumble_event()
                self.win_manager.update_gametype_wins(self.gametype)

                if self.check_fs_condition() and self.check_freespin_entry():
                    self.run_freespin_from_base()

            self.evaluate_finalwin()
            self.check_repeat()

        self.imprint_wins()

    def run_freespin(self):
        self.reset_fs_spin()
        while self.fs < self.tot_fs:
            self.update_freespin()
            self.xtile_position = None
            self.draw_board()
            self.maybe_spawn_xtile()

            self.get_clusters_update_wins()
            self.emit_tumble_win_events()

            while self.win_data["totalWin"] > 0 and not (self.wincap_triggered):
                self.tumble_game_board()
                self.get_clusters_update_wins()
                self.emit_tumble_win_events()

            self.set_end_tumble_event()
            self.win_manager.update_gametype_wins(self.gametype)

            if self.check_fs_condition():
                self.update_fs_retrigger_amt()

        self.end_freespin()
