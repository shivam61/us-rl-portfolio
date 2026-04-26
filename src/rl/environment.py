import gymnasium as gym
from gymnasium import spaces
import numpy as np

class PortfolioEnv(gym.Env):
    """
    Skeleton RL Environment for Portfolio Overlay.
    This environment does not pick stocks directly, but chooses sector tilts and cash target.
    """
    def __init__(self, n_sectors: int = 11):
        super().__init__()
        self.n_sectors = n_sectors
        
        # State: Macro (6) + Sector Scores (n_sectors) + Current Weights (n_sectors) + Cash (1) + Drawdown (1)
        obs_dim = 6 + n_sectors * 2 + 1 + 1
        self.observation_space = spaces.Box(low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32)
        
        # Action: Sector Tilt (-1 to 1 for each sector), Cash Target (0 to 1), Aggressiveness (0 to 1)
        action_dim = n_sectors + 1 + 1
        self.action_space = spaces.Box(low=-1.0, high=1.0, shape=(action_dim,), dtype=np.float32)
        
    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        obs = np.zeros(self.observation_space.shape, dtype=np.float32)
        info = {}
        return obs, info
        
    def step(self, action):
        obs = np.zeros(self.observation_space.shape, dtype=np.float32)
        reward = 0.0
        terminated = False
        truncated = False
        info = {}
        return obs, reward, terminated, truncated, info
