import os
import sys

sys.path.insert(0, os.path.dirname(__file__))


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: heavy v4 certification checks (full sweeps, rebuilds, 200-draw nulls, "
                                       "20k-draw bootstrap). Run with -m slow.")
