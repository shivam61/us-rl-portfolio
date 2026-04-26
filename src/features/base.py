import pandas as pd
from typing import Dict, Any

class BaseFeatureGenerator:
    def __init__(self, data_dict: Dict[str, pd.DataFrame], **kwargs: Any):
        self.data_dict = data_dict
        
    def generate(self) -> pd.DataFrame:
        """
        Returns a MultiIndex DataFrame (date, ticker) with generated features.
        All features MUST be shifted by at least 1 day to prevent leakage.
        """
        raise NotImplementedError
