from src.executables.executables import Executables
from src.calculations.cluster import Cluster
from src.calculations.symbol import Symbol
from src.wins.multiplier_strategy import apply_product_symbol_mult
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
        clusters: dict[str, list[list[tuple[int, int]]]],
        global_multiplier: int = 1,
        return_data: dict = {"totalWin": 0, "wins": []},
    ) -> tuple[list[list[Symbol]], dict]:
        """Evaluate clusters with size capped at config.max_cluster_pay_size."""
        max_size: int = config.max_cluster_pay_size
        multiplier_cap: int = getattr(config, "multiplier_product_cap", 1024)
        total_win: float = 0.0
        for sym in clusters:
            for cluster in clusters[sym]:
                actual_size: int = len(cluster)
                pay_size: int = min(actual_size, max_size)
                if (pay_size, sym) in config.paytable:
                    sym_win: float = config.paytable[(pay_size, sym)]
                    json_positions: list[dict[str, int]] = [{"reel": p[0], "row": p[1]} for p in cluster]
                    cluster_mult: int = apply_product_symbol_mult(
                        board, json_positions, cap=multiplier_cap
                    )
                    cluster_win: float = sym_win * cluster_mult * global_multiplier
                    total_win += cluster_win
                    central_pos: tuple[int, int] = Cluster.get_central_cluster_position(json_positions)
                    return_data["wins"].append(
                        {
                            "symbol": sym,
                            "clusterSize": actual_size,
                            "win": cluster_win,
                            "positions": json_positions,
                            "meta": {
                                "globalMult": global_multiplier,
                                "clusterMult": cluster_mult,
                                "winWithoutMult": sym_win,
                                "overlay": {"reel": central_pos[0], "row": central_pos[1]},
                            },
                        }
                    )
                    for positions in cluster:
                        board[positions[0]][positions[1]].explode = True

        return_data["totalWin"] += total_win
        return board, return_data
