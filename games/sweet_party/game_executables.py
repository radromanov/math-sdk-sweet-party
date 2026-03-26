import random

from game_calculations import GameCalculations
from src.calculations.cluster import Cluster
from src.calculations.statistics import get_random_outcome
from src.events.events import update_freespin_event, fs_trigger_event
from src.wins.multiplier_strategy import apply_product_symbol_mult
from game_events import xtile_spawn_event, xtile_apply_event


class GameExecutables(GameCalculations):
    """Game dependent grouped functions."""

    def _capped_scatter_count(self, scatter_key: str = "scatter") -> int:
        """Return scatter count capped to max key in freespin_triggers for current gametype."""
        raw_count: int = self.count_special_symbols(scatter_key)
        max_trigger: int = max(self.config.freespin_triggers[self.gametype].keys())
        return min(raw_count, max_trigger)

    def update_freespin_amount(self, scatter_key: str = "scatter") -> None:
        """Set initial number of spins, capping scatter count to max trigger key."""
        capped: int = self._capped_scatter_count(scatter_key)
        self.tot_fs = self.config.freespin_triggers[self.gametype][capped]
        if self.gametype == self.config.basegame_type:
            basegame_trigger, freegame_trigger = True, False
        else:
            basegame_trigger, freegame_trigger = False, True
        fs_trigger_event(self, basegame_trigger=basegame_trigger, freegame_trigger=freegame_trigger)

    def update_fs_retrigger_amt(self, scatter_key: str = "scatter") -> None:
        """Update total freespin amount on retrigger, capping scatter count."""
        capped: int = self._capped_scatter_count(scatter_key)
        self.tot_fs += self.config.freespin_triggers[self.gametype][capped]
        fs_trigger_event(self, freegame_trigger=True, basegame_trigger=False)

    # --- Gold X-Tile ---

    def maybe_spawn_xtile(self) -> None:
        """Roll to spawn a Gold X-Tile on a random board position if none exists."""
        if self.xtile_position is not None:
            return
        chance: float = self.config.xtile_chance.get(self.gametype, 0.0)
        if random.random() < chance:
            reel: int = random.randint(0, self.config.num_reels - 1)
            row: int = random.randint(0, self.config.num_rows[reel] - 1)
            self.xtile_position = (reel, row)
            xtile_spawn_event(self)

    def apply_xtile_to_clusters(self) -> None:
        """Grant random 2x/4x multipliers to all winning clusters that overlap the X-Tile.

        The X-Tile persists through the entire spin - it is NOT consumed on use.
        """
        if self.xtile_position is None:
            return
        xtile_reel: int = self.xtile_position[0]
        xtile_row: int = self.xtile_position[1]
        multiplier_cap: int = getattr(self.config, "multiplier_product_cap", 1024)

        for win_entry in self.win_data["wins"]:
            hit: bool = False
            for pos in win_entry["positions"]:
                if pos["reel"] == xtile_reel and pos["row"] == xtile_row:
                    hit = True
                    break
            if not hit:
                continue

            # Grant multipliers to symbols without native multipliers
            for pos in win_entry["positions"]:
                sym = self.board[pos["reel"]][pos["row"]]
                if sym.multiplier is None or sym.multiplier <= 1:
                    mult_value: int = get_random_outcome(self.config.multiplier_values)
                    sym.assign_attribute({"multiplier": mult_value, "has_multiplier": True})

            # Recalculate this cluster's win
            old_win: float = win_entry["win"]
            cluster_mult: int = apply_product_symbol_mult(
                self.board, win_entry["positions"], cap=multiplier_cap
            )
            sym_win: float = win_entry["meta"]["winWithoutMult"]
            new_win: float = sym_win * cluster_mult * win_entry["meta"]["globalMult"]
            win_entry["win"] = new_win
            win_entry["meta"]["clusterMult"] = cluster_mult
            self.win_data["totalWin"] += new_win - old_win

            xtile_apply_event(self, win_entry["symbol"], win_entry["positions"])

    # --- Cluster evaluation ---

    def get_clusters_update_wins(self) -> None:
        """Find clusters on board and update win manager."""
        clusters: dict = Cluster.get_clusters(self.board)
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

        if self.xtile_position is not None and self.win_data["totalWin"] > 0:
            self.apply_xtile_to_clusters()

        Cluster.record_cluster_wins(self)
        self.win_manager.update_spinwin(self.win_data["totalWin"])
        self.win_manager.tumble_win = self.win_data["totalWin"]

    def update_freespin(self) -> None:
        """Called before a new reveal during freegame."""
        self.fs += 1
        update_freespin_event(self)
        self.win_manager.reset_spin_win()
        self.win_data = {}
