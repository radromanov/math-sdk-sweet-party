from game_calculations import GameCalculations
from src.calculations.cluster import Cluster
from src.events.events import update_freespin_event, fs_trigger_event


class GameExecutables(GameCalculations):
    """Game dependent grouped functions."""

    def _capped_scatter_count(self, scatter_key: str = "scatter") -> int:
        """Return scatter count capped to max key in freespin_triggers for current gametype."""
        raw_count = self.count_special_symbols(scatter_key)
        max_trigger = max(self.config.freespin_triggers[self.gametype].keys())
        return min(raw_count, max_trigger)

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Set initial number of spins, capping scatter count to max trigger key."""
        capped = self._capped_scatter_count(scatter_key)
        self.tot_fs = self.config.freespin_triggers[self.gametype][capped]
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Update total freespin amount on retrigger, capping scatter count."""
        capped = self._capped_scatter_count(scatter_key)
        self.tot_fs += self.config.freespin_triggers[self.gametype][capped]
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    def get_clusters_update_wins(self) -> None:
        """Find clusters on board and update win manager."""
        clusters = Cluster.get_clusters(self.board)
        return_data: dict = {
            "totalWin": 0,
            "wins": [],
        }
        self.board, self.win_data = self.evaluate_clusters_capped(
            config=self.config,
            board=self.board,
            clusters=clusters,
            global_multiplier=self.global_multiplier,
            return_data=return_data,
        )

        Cluster.record_cluster_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.win_data = {}
