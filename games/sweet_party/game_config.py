"""Sweet Party cluster game configuration file/setup"""

import os
from src.config.config import Config
from src.config.distributions import Distribution
from src.config.betmode import BetMode


class GameConfig(Config):
    """Singleton cluster game configuration class."""

    _instance = None

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
        self.num_rows = [7] * self.num_reels

        # Paytable: h1-h7, cluster sizes 5-15
        pay_group = {
            # h1
            ((5, 5), "h1"): 2.0,
            ((6, 6), "h1"): 3.0,
            ((7, 7), "h1"): 3.5,
            ((8, 8), "h1"): 4.0,
            ((9, 9), "h1"): 5.0,
            ((10, 10), "h1"): 10.0,
            ((11, 11), "h1"): 15.0,
            ((12, 12), "h1"): 30.0,
            ((13, 13), "h1"): 70.0,
            ((14, 14), "h1"): 140.0,
            ((15, 15), "h1"): 300.0,
            # h2
            ((5, 5), "h2"): 1.5,
            ((6, 6), "h2"): 2.0,
            ((7, 7), "h2"): 2.5,
            ((8, 8), "h2"): 3.0,
            ((9, 9), "h2"): 4.0,
            ((10, 10), "h2"): 8.0,
            ((11, 11), "h2"): 12.0,
            ((12, 12), "h2"): 25.0,
            ((13, 13), "h2"): 60.0,
            ((14, 14), "h2"): 120.0,
            ((15, 15), "h2"): 200.0,
            # h3
            ((5, 5), "h3"): 1.0,
            ((6, 6), "h3"): 1.5,
            ((7, 7), "h3"): 2.0,
            ((8, 8), "h3"): 2.5,
            ((9, 9), "h3"): 3.0,
            ((10, 10), "h3"): 6.0,
            ((11, 11), "h3"): 9.0,
            ((12, 12), "h3"): 20.0,
            ((13, 13), "h3"): 50.0,
            ((14, 14), "h3"): 100.0,
            ((15, 15), "h3"): 180.0,
            # h4
            ((5, 5), "h4"): 0.8,
            ((6, 6), "h4"): 1.0,
            ((7, 7), "h4"): 1.5,
            ((8, 8), "h4"): 2.0,
            ((9, 9), "h4"): 2.5,
            ((10, 10), "h4"): 4.0,
            ((11, 11), "h4"): 6.0,
            ((12, 12), "h4"): 10.0,
            ((13, 13), "h4"): 40.0,
            ((14, 14), "h4"): 80.0,
            ((15, 15), "h4"): 160.0,
            # h5
            ((5, 5), "h5"): 0.6,
            ((6, 6), "h5"): 0.8,
            ((7, 7), "h5"): 1.0,
            ((8, 8), "h5"): 1.5,
            ((9, 9), "h5"): 2.0,
            ((10, 10), "h5"): 3.0,
            ((11, 11), "h5"): 5.0,
            ((12, 12), "h5"): 7.0,
            ((13, 13), "h5"): 30.0,
            ((14, 14), "h5"): 60.0,
            ((15, 15), "h5"): 120.0,
            # h6
            ((5, 5), "h6"): 0.5,
            ((6, 6), "h6"): 0.6,
            ((7, 7), "h6"): 0.8,
            ((8, 8), "h6"): 1.0,
            ((9, 9), "h6"): 1.5,
            ((10, 10), "h6"): 2.5,
            ((11, 11), "h6"): 4.0,
            ((12, 12), "h6"): 6.0,
            ((13, 13), "h6"): 20.0,
            ((14, 14), "h6"): 40.0,
            ((15, 15), "h6"): 80.0,
            # h7
            ((5, 5), "h7"): 0.4,
            ((6, 6), "h7"): 0.5,
            ((7, 7), "h7"): 0.6,
            ((8, 8), "h7"): 0.8,
            ((9, 9), "h7"): 1.0,
            ((10, 10), "h7"): 2.0,
            ((11, 11), "h7"): 3.0,
            ((12, 12), "h7"): 5.0,
            ((13, 13), "h7"): 10.0,
            ((14, 14), "h7"): 20.0,
            ((15, 15), "h7"): 40.0,
        }
        self.paytable = self.convert_range_table(pay_group)

        self.include_padding = True
        self.special_symbols = {"wild": [], "scatter": ["S"]}

        self.freespin_triggers = {
            self.basegame_type: {3: 8, 4: 10, 5: 11, 6: 12, 7: 13},
            self.freegame_type: {3: 6, 4: 8, 5: 10, 6: 12, 7: 14},
        }
        self.anticipation_triggers = {
            self.basegame_type: min(self.freespin_triggers[self.basegame_type].keys()) - 1,
            self.freegame_type: min(self.freespin_triggers[self.freegame_type].keys()) - 1,
        }

        self.max_cluster_pay_size = 15

        reels = {"BR0": "BR0.csv", "FR0": "FR0.csv", "WCAP": "WCAP.csv"}
        self.reels = {}
        for r, f in reels.items():
            self.reels[r] = self.read_reels_csv(os.path.join(self.reels_path, f))
        mode_maxwins = {"base": 10000}

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
                            "scatter_triggers": {3: 1, 4: 2, 5: 3, 6: 2, 7: 1},
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
                            "scatter_triggers": {3: 5, 4: 2, 5: 1, 6: 1, 7: 1},
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
                        quota=0.499,
                        conditions={
                            "reel_weights": {self.basegame_type: {"BR0": 1}},
                            "force_wincap": False,
                            "force_freegame": False,
                        },
                    ),
                ],
            ),
        ]
