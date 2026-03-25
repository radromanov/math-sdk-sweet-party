"""Set conditions/parameters for optimization program"""

from optimization_program.optimization_config import (
    ConstructScaling,
    ConstructParameters,
    ConstructFenceBias,
    ConstructConditions,
    verify_optimization_input,
)


class OptimizationSetup:
    """"""

    def __init__(self, game_config):
        self.game_config = game_config
        wincaps = {}
        for bm in game_config.bet_modes:
            wincaps[bm.get_name()] = bm.get_wincap()

        base_scaling = ConstructScaling(
            [
                {"criteria": "basegame", "scale_factor": 1.2, "win_range": (1, 2), "probability": 1.0},
                {"criteria": "basegame", "scale_factor": 1.5, "win_range": (10, 20), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 0.8, "win_range": (1000, 2000), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 1.2, "win_range": (3000, 4000), "probability": 1.0},
            ]
        ).return_dict()

        base_parameters = ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[50, 100, 200],
            test_weights=[0.3, 0.4, 0.3],
            score_type="rtp",
        ).return_dict()

        base_distribution_bias = ConstructFenceBias(
            applied_criteria=["basegame"],
            bias_ranges=[(0.5, 1.5)],
            bias_weights=[0.4],
        ).return_dict()

        bonus_scaling = ConstructScaling(
            [
                {"criteria": "freegame", "scale_factor": 0.9, "win_range": (20, 50), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 0.8, "win_range": (1000, 2000), "probability": 1.0},
                {"criteria": "freegame", "scale_factor": 1.2, "win_range": (3000, 4000), "probability": 1.0},
            ]
        ).return_dict()

        bonus_parameters = ConstructParameters(
            num_show=5000,
            num_per_fence=10000,
            min_m2m=4,
            max_m2m=8,
            pmb_rtp=1.0,
            sim_trials=5000,
            test_spins=[10, 20, 50],
            test_weights=[0.6, 0.2, 0.2],
            score_type="rtp",
        ).return_dict()

        self.game_config.opt_params = {
            "base": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=wincaps["base"], search_conditions=wincaps["base"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.36, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.59).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": base_distribution_bias,
            },
            # STUB: RTP splits for feature_5x are placeholders - require calibration
            "feature_5x": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=wincaps["feature_5x"], search_conditions=wincaps["feature_5x"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.36, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.59).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": base_distribution_bias,
            },
            # STUB: RTP splits for feature_cluster_drop are placeholders - require calibration
            "feature_cluster_drop": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=wincaps["feature_cluster_drop"], search_conditions=wincaps["feature_cluster_drop"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.36, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.59).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": base_distribution_bias,
            },
            # STUB: RTP splits for feature_max_multi_tile are placeholders - require calibration
            "feature_max_multi_tile": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=wincaps["feature_max_multi_tile"], search_conditions=wincaps["feature_max_multi_tile"]
                    ).return_dict(),
                    "0": ConstructConditions(rtp=0, av_win=0, search_conditions=0).return_dict(),
                    "freegame": ConstructConditions(
                        rtp=0.36, hr=200, search_conditions={"symbol": "scatter"}
                    ).return_dict(),
                    "basegame": ConstructConditions(hr=3.5, rtp=0.59).return_dict(),
                },
                "scaling": base_scaling,
                "parameters": base_parameters,
                "distribution_bias": base_distribution_bias,
            },
            "bonus": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=wincaps["bonus"], search_conditions=wincaps["bonus"]
                    ).return_dict(),
                    "freegame": ConstructConditions(rtp=0.95).return_dict(),
                },
                "scaling": bonus_scaling,
                "parameters": bonus_parameters,
            },
            # STUB: RTP splits for super_bonus are placeholders - require calibration
            "super_bonus": {
                "conditions": {
                    "wincap": ConstructConditions(
                        rtp=0.01, av_win=wincaps["super_bonus"], search_conditions=wincaps["super_bonus"]
                    ).return_dict(),
                    "freegame": ConstructConditions(rtp=0.95).return_dict(),
                },
                "scaling": bonus_scaling,
                "parameters": bonus_parameters,
            },
        }

        verify_optimization_input(self.game_config, self.game_config.opt_params)
