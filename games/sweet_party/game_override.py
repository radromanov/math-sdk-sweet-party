import random

from game_executables import GameExecutables
from src.calculations.symbol import Symbol
from src.calculations.statistics import get_random_outcome


class GameStateOverride(GameExecutables):
    """
    This class is used to override or extend universal state.py functions.
    e.g: A specific game may have custom book properties to reset
    """

    def reset_book(self) -> None:
        super().reset_book()
        self.tumble_win = 0
        self.xtile_position: tuple[int, int] | None = None

    def assign_special_sym_function(self) -> None:
        """Register random multiplier assignment for all paying symbols."""
        paying_symbols: set[str] = set()
        for _, sym in self.config.paytable:
            paying_symbols.add(sym)

        for sym_name in paying_symbols:
            if sym_name not in self.config.multiplier_excluded_symbols:
                self.special_symbol_functions.setdefault(sym_name, []).append(
                    self._maybe_assign_multiplier
                )

    def _maybe_assign_multiplier(self, symbol: Symbol) -> None:
        """Randomly assign a 2x or 4x multiplier to a symbol."""
        if random.random() < self.config.multiplier_chance:
            mult_value: int = get_random_outcome(self.config.multiplier_values)
            symbol.assign_attribute({"multiplier": mult_value, "has_multiplier": True})

    def check_repeat(self) -> None:
        """Checks if the spin failed a criteria constraint at any point."""
        if self.repeat is False:
            win_criteria = self.get_current_betmode_distributions().get_win_criteria()
            if win_criteria is not None and self.final_win != win_criteria:
                self.repeat = True

            if self.get_current_distribution_conditions()["force_freegame"] and not (self.triggered_freegame):
                self.repeat = True

            if self.win_manager.running_bet_win == 0 and self.criteria != "0":
                self.repeat = True
