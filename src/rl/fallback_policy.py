import pandas as pd

class RuleBasedFallbackPolicy:
    """
    When RL is disabled, this policy acts as a pass-through or applies static rules.
    """
    def __init__(self, cash_target: float = 0.0):
        self.cash_target = cash_target
        
    def get_action(self, state: pd.Series) -> dict:
        """
        Returns tilts and cash targets.
        """
        return {
            "sector_tilts": {},  # No tilts, trust optimizer
            "cash_target": self.cash_target,
            "aggressiveness": 1.0
        }
