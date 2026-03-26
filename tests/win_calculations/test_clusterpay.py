"""Test basic cluster-calculation functionality."""

import pytest
from tests.win_calculations.game_test_config import GamestateTest, create_blank_board
from src.calculations.cluster import Cluster
from src.wins.multiplier_strategy import apply_product_symbol_mult


class GameClusterConfig:
    """Testing game functions"""

    def __init__(self):
        self.game_id = "0_test_class"
        self.rtp = 0.9700

        # Game Dimensions
        self.num_reels = 6
        self.num_rows = [6] * self.num_reels
        # Board and Symbol Properties
        t1, t2, t3, t4 = (5, 5), (6, 8), (9, 12), (13, 36)
        pay_group = {
            (t1, "H1"): 5.0,
            (t2, "H1"): 12.5,
            (t3, "H1"): 25.0,
            (t4, "H1"): 60.0,
            (t1, "H2"): 5.0,
            (t2, "H2"): 12.5,
            (t3, "H2"): 25.0,
            (t4, "H2"): 60.0,
        }
        self.paytable = convert_range_table(pay_group)

        self.special_symbols = {"wild": ["WM"], "scatter": ["S"], "multiplier": ["WM"], "blank": ["X"]}
        self.bet_modes = []
        self.basegame_type = "basegame"
        self.freegame_type = "freegame"


def convert_range_table(pay_group: dict) -> dict:
    paytable = {}
    for sym_details, payout in pay_group.items():
        min_connections, max_connections = sym_details[0][0], sym_details[0][1]
        symbol = sym_details[1]
        for i in range(min_connections, max_connections + 1):
            paytable[(i, symbol)] = payout

    return paytable


def create_test_cluster_gamestate():
    """Boilerplate gamestate for testing."""
    test_config = GameClusterConfig()
    test_gamestate = GamestateTest(test_config)
    test_gamestate.create_symbol_map()
    test_gamestate.assign_special_sym_function()
    test_gamestate.board = create_blank_board(test_config.num_reels, test_config.num_rows)

    return test_gamestate


@pytest.fixture(scope="function")
def gamestate():
    return create_test_cluster_gamestate()


def test_wild_mult_cluster(gamestate):
    for idx, _ in enumerate(gamestate.board):
        for idy, _ in enumerate(gamestate.board[idx]):
            if idx < 4 and idy < 4:
                gamestate.board[idx][idy] = gamestate.create_symbol("WM")
            else:
                gamestate.board[idx][idy] = gamestate.create_symbol("X")
    gamestate.board[0][4] = gamestate.create_symbol("H1")
    # Expect 10-size wilds with mult defaulting to H1 payout

    clusters = Cluster.get_clusters(gamestate.board)
    _, win_data, total_win = Cluster.evaluate_clusters(
        config=gamestate.config,
        board=gamestate.board,
        clusters=clusters,
    )
    assert total_win == (
        gamestate.config.paytable[(17, "H1")] * sum([3 for _ in range(len(win_data["wins"][0]["positions"]) - 1)])
    )


def test_basic_cluster(gamestate):
    for idx, _ in enumerate(gamestate.board):
        for idy, _ in enumerate(gamestate.board[idx]):
            # 3x3 grid of same symbol
            if idx < 3 and idy < 3:
                gamestate.board[idx][idy] = gamestate.create_symbol("H1")
            else:
                gamestate.board[idx][idy] = gamestate.create_symbol("X")

    clusters = Cluster.get_clusters(gamestate.board)
    _, _, total_win = Cluster.evaluate_clusters(
        config=gamestate.config,
        board=gamestate.board,
        clusters=clusters,
    )
    assert total_win == gamestate.config.paytable[(9, "H1")]


# --- Symbol multiplier (product) tests using evaluate_clusters_capped ---


class CappedClusterConfig:
    """Config for testing evaluate_clusters_capped with multipliers."""

    def __init__(self) -> None:
        self.game_id: str = "capped_test"
        self.rtp: float = 0.96
        self.num_reels: int = 6
        self.num_rows: list[int] = [6] * self.num_reels
        t1: tuple[int, int] = (5, 5)
        t2: tuple[int, int] = (6, 15)
        pay_group: dict = {
            (t1, "H1"): 5.0,
            (t2, "H1"): 12.5,
            (t1, "H2"): 3.0,
            (t2, "H2"): 8.0,
        }
        self.paytable: dict = convert_range_table(pay_group)
        self.special_symbols: dict[str, list[str]] = {
            "wild": [],
            "scatter": [],
            "multiplier": [],
            "blank": ["X"],
        }
        self.bet_modes: list = []
        self.basegame_type: str = "basegame"
        self.freegame_type: str = "freegame"
        self.max_cluster_pay_size: int = 15
        self.multiplier_product_cap: int = 1024


def evaluate_clusters_capped(config, board, clusters, global_multiplier=1, return_data=None):
    """Local copy of game-specific cluster evaluation for testing (avoids game_config import)."""
    if return_data is None:
        return_data = {"totalWin": 0, "wins": []}
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
                central_pos = Cluster.get_central_cluster_position(json_positions)
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


def create_capped_gamestate() -> GamestateTest:
    """Boilerplate gamestate for capped cluster tests."""
    config: CappedClusterConfig = CappedClusterConfig()
    gs: GamestateTest = GamestateTest(config)
    gs.create_symbol_map()
    gs.special_symbol_functions = {}
    gs.board = create_blank_board(config.num_reels, config.num_rows)
    return gs


@pytest.fixture(scope="function")
def capped_gs() -> GamestateTest:
    return create_capped_gamestate()


def _fill_blank(gs: GamestateTest) -> None:
    """Fill entire board with blank symbols."""
    for idx in range(len(gs.board)):
        for idy in range(len(gs.board[idx])):
            gs.board[idx][idy] = gs.create_symbol("X")


def test_single_2x_multiplier(capped_gs: GamestateTest) -> None:
    """One symbol with 2x in a 5-cluster -> win = paytable * 2."""
    _fill_blank(capped_gs)
    for i in range(3):
        capped_gs.board[0][i] = capped_gs.create_symbol("H1")
    capped_gs.board[1][0] = capped_gs.create_symbol("H1")
    capped_gs.board[2][0] = capped_gs.create_symbol("H1")

    capped_gs.board[0][0].assign_attribute({"multiplier": 2, "has_multiplier": True})

    clusters: dict = Cluster.get_clusters(capped_gs.board)
    _, result = evaluate_clusters_capped(
        config=capped_gs.config,
        board=capped_gs.board,
        clusters=clusters,
    )
    base_win: float = capped_gs.config.paytable[(5, "H1")]
    assert result["totalWin"] == base_win * 2
    assert result["wins"][0]["meta"]["clusterMult"] == 2


def test_product_of_multipliers(capped_gs: GamestateTest) -> None:
    """Three multipliers (2x, 2x, 4x) -> product = 16."""
    _fill_blank(capped_gs)
    for i in range(3):
        capped_gs.board[0][i] = capped_gs.create_symbol("H1")
    capped_gs.board[1][0] = capped_gs.create_symbol("H1")
    capped_gs.board[2][0] = capped_gs.create_symbol("H1")

    capped_gs.board[0][0].assign_attribute({"multiplier": 2, "has_multiplier": True})
    capped_gs.board[0][1].assign_attribute({"multiplier": 2, "has_multiplier": True})
    capped_gs.board[1][0].assign_attribute({"multiplier": 4, "has_multiplier": True})

    clusters: dict = Cluster.get_clusters(capped_gs.board)
    _, result = evaluate_clusters_capped(
        config=capped_gs.config,
        board=capped_gs.board,
        clusters=clusters,
    )
    base_win: float = capped_gs.config.paytable[(5, "H1")]
    assert result["totalWin"] == base_win * 16
    assert result["wins"][0]["meta"]["clusterMult"] == 16


def test_multiplier_product_cap(capped_gs: GamestateTest) -> None:
    """Product exceeding 1024 is capped."""
    _fill_blank(capped_gs)
    for i in range(6):
        capped_gs.board[0][i] = capped_gs.create_symbol("H1")
    for i in range(5):
        capped_gs.board[1][i] = capped_gs.create_symbol("H1")

    # 4^11 = 4194304, capped at 1024
    for i in range(6):
        capped_gs.board[0][i].assign_attribute({"multiplier": 4, "has_multiplier": True})
    for i in range(5):
        capped_gs.board[1][i].assign_attribute({"multiplier": 4, "has_multiplier": True})

    clusters: dict = Cluster.get_clusters(capped_gs.board)
    _, result = evaluate_clusters_capped(
        config=capped_gs.config,
        board=capped_gs.board,
        clusters=clusters,
    )
    base_win: float = capped_gs.config.paytable[(11, "H1")]
    assert result["totalWin"] == base_win * 1024
    assert result["wins"][0]["meta"]["clusterMult"] == 1024


def test_no_multipliers_default(capped_gs: GamestateTest) -> None:
    """Cluster with no multipliers -> clusterMult = 1, same as base win."""
    _fill_blank(capped_gs)
    for i in range(3):
        capped_gs.board[0][i] = capped_gs.create_symbol("H1")
    capped_gs.board[1][0] = capped_gs.create_symbol("H1")
    capped_gs.board[2][0] = capped_gs.create_symbol("H1")

    clusters: dict = Cluster.get_clusters(capped_gs.board)
    _, result = evaluate_clusters_capped(
        config=capped_gs.config,
        board=capped_gs.board,
        clusters=clusters,
    )
    base_win: float = capped_gs.config.paytable[(5, "H1")]
    assert result["totalWin"] == base_win
    assert result["wins"][0]["meta"]["clusterMult"] == 1


def test_multipliers_on_non_winning_symbols_ignored(capped_gs: GamestateTest) -> None:
    """Multipliers on symbols outside the winning cluster have no effect."""
    _fill_blank(capped_gs)
    for i in range(3):
        capped_gs.board[0][i] = capped_gs.create_symbol("H1")
    capped_gs.board[1][0] = capped_gs.create_symbol("H1")
    capped_gs.board[2][0] = capped_gs.create_symbol("H1")

    capped_gs.board[5][5].assign_attribute({"multiplier": 4, "has_multiplier": True})

    clusters: dict = Cluster.get_clusters(capped_gs.board)
    _, result = evaluate_clusters_capped(
        config=capped_gs.config,
        board=capped_gs.board,
        clusters=clusters,
    )
    base_win: float = capped_gs.config.paytable[(5, "H1")]
    assert result["totalWin"] == base_win
    assert result["wins"][0]["meta"]["clusterMult"] == 1
