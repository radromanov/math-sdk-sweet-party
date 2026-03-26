from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.symbol import Symbol
from game_config import GameConfig


class GameCalculations(Executables):
    """
    Game-specific cluster evaluation.
    Caps cluster sizes at max_cluster_pay_size so oversized clusters
    still pay at the highest paytable tier.
    """

    @staticmethod
    def evaluate_clusters_capped(
        config: GameConfig,
        board: list[list[Symbol]],
        clusters: dict,
        global_multiplier: int = 1,
        return_data: dict = {"totalWin": 0, "wins": []},
    ) -> tuple:
        """Evaluate clusters with size capped at config.max_cluster_pay_size."""
        max_size: int = config.max_cluster_pay_size
        total_win = 0.0
        for sym in clusters:
            for cluster in clusters[sym]:
                actual_size = len(cluster)
                pay_size = min(actual_size, max_size)
                if (pay_size, sym) in config.paytable:
                    sym_win = config.paytable[(pay_size, sym)]
                    cluster_win = sym_win * global_multiplier
                    total_win += cluster_win
                    json_positions = [{"reel": p[0], "row": p[1]} for p in cluster]
                    central_pos = Cluster.get_central_cluster_position(json_positions)
                    return_data["wins"].append(
                        {
                            "symbol": sym,
                            "clusterSize": actual_size,
                            "win": cluster_win,
                            "positions": json_positions,
                            "meta": {
                                "globalMult": global_multiplier,
                                "clusterMult": 1,
                                "winWithoutMult": sym_win,
                                "overlay": {"reel": central_pos[0], "row": central_pos[1]},
                            },
                        }
                    )
                    for positions in cluster:
                        board[positions[0]][positions[1]].explode = True

        return_data["totalWin"] += total_win
        return board, return_data
