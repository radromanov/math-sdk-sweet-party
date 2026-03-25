from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.board import Board
from game_config import GameConfig


class GameCalculations(Executables):
    """
    Overrides cluster evaluation to use per-symbol 2x/4x multipliers.
    Cluster multiplier = product of all symbol multipliers in the cluster,
    capped at config.maximum_board_mult (1024).
    """

    def evaluate_clusters(
        self,
        config: GameConfig,
        board: Board,
        clusters: dict,
        global_multiplier: int = 1,
        x_tile_position: tuple | None = None,
        return_data: dict = {"totalWin": 0, "wins": []},
    ) -> tuple:
        """
        Determine payout from each cluster.
        If a cluster overlaps the Gold X-Tile, every symbol in that cluster
        which has no multiplier is assigned one (stubbed at 2x).
        The cluster multiplier is the product of all symbol multipliers, capped at
        maximum_board_mult.
        """
        exploding_symbols = []
        total_win = 0

        for sym in clusters:
            for cluster in clusters[sym]:
                syms_in_cluster = len(cluster)
                if (syms_in_cluster, sym) not in config.paytable:
                    continue

                # Check if any position in this cluster lands on the Gold X-Tile
                if x_tile_position is not None and any(
                    p[0] == x_tile_position[0] and p[1] == x_tile_position[1]
                    for p in cluster
                ):
                    self.x_tile_cluster_hit = True
                    # Assign a multiplier to every unassigned symbol in this cluster
                    for p in cluster:
                        sym_obj = board[p[0]][p[1]]
                        if sym_obj.multiplier is None:
                            sym_obj.multiplier = 2  # STUB: X-Tile default multiplier unknown

                # Cluster multiplier = product of all symbol multipliers (None counts as 1)
                cluster_mult = 1
                for p in cluster:
                    m = board[p[0]][p[1]].multiplier
                    if m is not None:
                        cluster_mult *= m
                cluster_mult = min(cluster_mult, config.maximum_board_mult)

                sym_win = config.paytable[(syms_in_cluster, sym)]
                total_sym_win = sym_win * cluster_mult * global_multiplier
                total_win += total_sym_win

                json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]
                central_pos = Cluster.get_central_cluster_position(json_positions)
                return_data["wins"].append(
                    {
                        "symbol": sym,
                        "clusterSize": syms_in_cluster,
                        "win": total_sym_win,
                        "positions": json_positions,
                        "meta": {
                            "globalMult": global_multiplier,
                            "clusterMult": cluster_mult,
                            "winWithoutMult": sym_win,
                            "overlay": {"reel": central_pos[0], "row": central_pos[1]},
                        },
                    }
                )

                for p in cluster:
                    board[p[0]][p[1]].explode = True
                    pos_dict = {"reel": p[0], "row": p[1]}
                    if pos_dict not in exploding_symbols:
                        exploding_symbols.append(pos_dict)

        return_data["totalWin"] += total_win
        return board, return_data
