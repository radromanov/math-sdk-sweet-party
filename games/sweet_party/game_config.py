import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Singleton cluster game configuration class."""

    _instance = None
    super_basegame_type = "super_basegame_type"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        super().__init__()
        self.game_id = "sweet_party"
        self.provider_number = 0
        self.working_name = "Sweet Party"
        self.wincap = 10000.0
        self.win_type = "cluster"
        self.rtp = 0.9600
        self.construct_paths()

        # Game Dimensions
        self.num_reels = 7
        # Optionally include variable number of rows per reel
        self.num_rows = [7] * self.num_reels
        # Board and Symbol Properties
        t1, t2, t3, t4, t5, t6, t7, t8, t9, t10, t11 = (5,5), (6,6), (7,7), (8,8), (9,9), (10,10), (11,11), (12,12), (13,13), (14,14), (15,15)
        pay_group = {
            # H1
            (t1,  "h1"): 2.0,
            (t2,  "h1"): 3.0,
            (t3,  "h1"): 3.5,
            (t4,  "h1"): 4.0,
            (t5,  "h1"): 5.0,
            (t6,  "h1"): 10.0,
            (t7,  "h1"): 15.0,
            (t8,  "h1"): 30.0,
            (t9,  "h1"): 70.0,
            (t10, "h1"): 140.0,
            (t11, "h1"): 300.0,

            # H2
            (t1,  "h2"): 1.5,
            (t2,  "h2"): 2.0,
            (t3,  "h2"): 2.5,
            (t4,  "h2"): 3.0,
            (t5,  "h2"): 4.0,
            (t6,  "h2"): 8.0,
            (t7,  "h2"): 12.0,
            (t8,  "h2"): 25.0,
            (t9,  "h2"): 60.0,
            (t10, "h2"): 120.0,
            (t11, "h2"): 200.0,

            # H3
            (t1,  "h3"): 1.0,
            (t2,  "h3"): 1.5,
            (t3,  "h3"): 2.0,
            (t4,  "h3"): 2.5,
            (t5,  "h3"): 3.0,
            (t6,  "h3"): 6.0,
            (t7,  "h3"): 9.0,
            (t8,  "h3"): 20.0,
            (t9,  "h3"): 50.0,
            (t10, "h3"): 100.0,
            (t11, "h3"): 180.0,

            # H4
            (t1,  "h4"): 0.8,
            (t2,  "h4"): 1.0,
            (t3,  "h4"): 1.5,
            (t4,  "h4"): 2.0,
            (t5,  "h4"): 2.5,
            (t6,  "h4"): 4.0,
            (t7,  "h4"): 6.0,
            (t8,  "h4"): 10.0,
            (t9,  "h4"): 40.0,
            (t10, "h4"): 80.0,
            (t11, "h4"): 160.0,

            # H5
            (t1,  "h5"): 0.6,
            (t2,  "h5"): 0.8,
            (t3,  "h5"): 1.0,
            (t4,  "h5"): 1.5,
            (t5,  "h5"): 2.0,
            (t6,  "h5"): 3.0,
            (t7,  "h5"): 5.0,
            (t8,  "h5"): 7.0,
            (t9,  "h5"): 30.0,
            (t10, "h5"): 60.0,
            (t11, "h5"): 120.0,

            # H6
            (t1,  "h6"): 0.5,
            (t2,  "h6"): 0.6,
            (t3,  "h6"): 0.8,
            (t4,  "h6"): 1.0,
            (t5,  "h6"): 1.5,
            (t6,  "h6"): 2.5,
            (t7,  "h6"): 4.0,
            (t8,  "h6"): 6.0,
            (t9,  "h6"): 20.0,
            (t10, "h6"): 40.0,
            (t11, "h6"): 80.0,

            # H7
            (t1,  "h7"): 0.4,
            (t2,  "h7"): 0.5,
            (t3,  "h7"): 0.6,
            (t4,  "h7"): 0.8,
            (t5,  "h7"): 1.0,
            (t6,  "h7"): 2.0,
            (t7,  "h7"): 3.0,
            (t8,  "h7"): 5.0,
            (t9,  "h7"): 10.0,
            (t10, "h7"): 20.0,
            (t11, "h7"): 40.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        self.special_symbols = {"scatter": ["S"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 8}, # Standard bonus
            self.super_basegame_type: {4: 10, 5: 11, 6: 12, 7: 13}, # Super bonus
            self.freegame_type: {3: 6, 4: 8, 5: 10, 6: 12, 7: 14}, # Retriggers
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.super_basegame_type: min(self.freespin_triggers[self.super_basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        self.maximum_board_mult = 1024

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))
        mode_maxwins = {
            "base": 10000,
            "bonus": 10000,
            "super_bonus": 10000,
            "feature_5x": 10000,
            "feature_cluster_drop": 10000,
            "feature_max_multi_tile": 10000,
        }

        self.bet_modes = [
            BetMode(
                name="base",
                cost=1.0,
                rtp=self.rtp,
                max_win=mode_maxwins["base"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["base"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 5, 5: 1},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            # FEATURE_5X: 5x more scatter chance, cost = 3x base bet
            BetMode(
                name="feature_5x",
                cost=3.0,
                rtp=self.rtp,
                max_win=mode_maxwins["feature_5x"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["feature_5x"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},  # STUB: dedicated reel strip unknown
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "scatter_triggers": {4: 5, 5: 10},  # STUB: ~5x boost vs base {4:1, 5:2}
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},  # STUB
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 25, 5: 5},  # STUB: ~5x boost vs base {4:5, 5:1}
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},  # STUB
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},  # STUB
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            # FEATURE_Cluster_Drop: guaranteed cluster per spin, cost = 25x base bet
            BetMode(
                name="feature_cluster_drop",
                cost=25.0,
                rtp=self.rtp,
                max_win=mode_maxwins["feature_cluster_drop"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["feature_cluster_drop"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},  # STUB: dedicated reel strip unknown
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            # "force_cluster": True,  # STUB: engine condition key unknown
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},  # STUB
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 5, 5: 1},
                            # "force_cluster": True,  # STUB: engine condition key unknown
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},  # STUB
                            # "force_cluster": True,  # STUB
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},  # STUB
                            # "force_cluster": True,  # STUB
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            # FEATURE_Max_Multi_Tile: guaranteed cluster landing on Gold X-Tile, cost = 500x base bet
            BetMode(
                name="feature_max_multi_tile",
                cost=500.0,
                rtp=self.rtp,
                max_win=mode_maxwins["feature_max_multi_tile"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=False,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["feature_max_multi_tile"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},  # STUB: dedicated reel strip unknown
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            # "force_x_tile_cluster": True,  # STUB: engine condition key unknown
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},  # STUB
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 5, 5: 1},
                            # "force_x_tile_cluster": True,  # STUB: engine condition key unknown
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="0",
                        quota=0.4,
                        win_criteria=0.0,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},  # STUB
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                    Distribution(
                        criteria="basegame",
                        quota=0.5,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},  # STUB
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
            # BONUS: 8 free spins, triggered by 3 scatters in base game or bought directly
            BetMode(
                name="bonus",
                cost=100.0,
                rtp=self.rtp,
                max_win=mode_maxwins["bonus"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["bonus"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {  # STUB: actual weights unknown — see missing_info.md
                                self.basegame_type: {2: 10, 3: 20, 4: 30, 5: 20, 10: 20, 20: 20, 50: 10},
                                self.freegame_type: {2: 10, 3: 20, 4: 30, 5: 20, 10: 20, 20: 20, 50: 10},
                            },
                            "scatter_triggers": {4: 1, 5: 2},
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {4: 5, 5: 1},
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
            # SUPER_BONUS: 10-13 free spins (4-7 scatters), triggered in base game or bought directly
            BetMode(
                name="super_bonus",
                cost=300.0,
                rtp=self.rtp,
                max_win=mode_maxwins["super_bonus"],
                auto_close_disabled=False,
                is_feature=True,
                is_buybonus=True,
                distributions=[
                    Distribution(
                        criteria="wincap",
                        quota=0.001,
                        win_criteria=mode_maxwins["super_bonus"],
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},  # STUB: dedicated reel strip unknown
                                self.freegame_type: {"FR0": 1, "WCAP": 5},
                            },
                            "mult_values": {  # STUB: actual weights unknown — see missing_info.md
                                self.basegame_type: {2: 10, 3: 20, 4: 30, 5: 20, 10: 20, 20: 20, 50: 10},
                                self.freegame_type: {2: 10, 3: 20, 4: 30, 5: 20, 10: 20, 20: 20, 50: 10},
                            },
                            "scatter_triggers": {5: 1, 6: 2, 7: 3},  # STUB: relative weights unknown
                            "force_wincap": True,
                            "force_freegame": True,
                        },
                    ),
                    Distribution(
                        criteria="freegame",
                        quota=0.1,
                        conditions={
                            "reel_weights": {
                                self.basegame_type: {"BR0": 1},  # STUB
                                self.freegame_type: {"FR0": 1},
                            },
                            "scatter_triggers": {5: 5, 6: 2, 7: 1},  # STUB: relative weights unknown
                            "force_wincap": False,
                            "force_freegame": True,
                        },
                    ),
                ],
            ),
        ]
