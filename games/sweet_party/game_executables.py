import random

from game_calculations import GameCalculations
from src.calculations.cluster import Cluster
from src.calculations.statistics import get_random_outcome
from src.events.events import update_freespin_event


class GameExecutables(GameCalculations):
    """Game dependent grouped functions."""

    def assign_symbol_multipliers(self) -> None:
        """Randomly assign 2x or 4x multipliers to non-scatter symbols that don't yet have one.
        Called after draw_board() and after each tumble to cover newly revealed symbols."""
        for reel in range(self.config.num_reels):
            for row in range(self.config.num_rows[reel]):
                sym = self.board[reel][row]
                if not sym.scatter and sym.multiplier is None:
                    sym.multiplier = get_random_outcome(self.config.symbol_mult_weights)

    def spawn_x_tile(self) -> None:
        """Spawn a Gold X-Tile at a random board position.
        Probability is determined by the active game type and bet mode:
        - SUPER_BONUS freespins: 100% guaranteed
        - BONUS freespins (freegame_type): 10%
        - Base game: 0% (TODO)
        """
        if self.betmode == "super_bonus" and self.gametype == self.config.freegame_type:
            prob = 1.0
        else:
            prob = self.config.x_tile_probabilities.get(self.gametype, 0.0)

        if prob > 0.0 and random.random() < prob:
            reel = random.randrange(self.config.num_reels)
            row = random.randrange(self.config.num_rows[reel])
            self.x_tile_position = (reel, row)
        else:
            self.x_tile_position = None

    def get_clusters_update_wins(self) -> None:
        """Find clusters on board and update win manager."""
        clusters = Cluster.get_clusters(self.board, "wild")
        return_data = {"totalWin": 0, "wins": []}
        self.x_tile_cluster_hit = False
        self.board, self.win_data = self.evaluate_clusters(
            config=self.config,
            board=self.board,
            clusters=clusters,
            global_multiplier=self.global_multiplier,
            x_tile_position=self.x_tile_position,
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
        self.tumblewin_mult = 0
        self.win_data = {}
