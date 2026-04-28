import pandas as pd

from src.alpha import build_alpha_score_provider, compute_volatility_score_frame
from src.config.loader import AlphaConfig


def test_alpha_default_score_is_volatility():
    assert AlphaConfig().default_score == "volatility_score"


def test_compute_volatility_score_frame_prefers_riskier_names():
    index = pd.MultiIndex.from_product(
        [pd.to_datetime(["2020-01-31"]), ["LOW", "HIGH"]],
        names=["date", "ticker"],
    )
    panel = pd.DataFrame(
        {
            "volatility_63d": [0.10, 0.30],
            "downside_vol_63d": [0.08, 0.25],
            "beta_to_spy_63d": [0.90, 1.40],
            "max_drawdown_63d": [-0.05, -0.20],
        },
        index=index,
    )

    scores = compute_volatility_score_frame(panel)

    assert scores.loc[(pd.Timestamp("2020-01-31"), "HIGH"), "volatility_score"] > scores.loc[(pd.Timestamp("2020-01-31"), "LOW"), "volatility_score"]
    assert scores.loc[(pd.Timestamp("2020-01-31"), "HIGH"), "volatility_score_rank"] == 1.0


def test_build_alpha_score_provider_ffills_to_latest_available_date():
    index = pd.MultiIndex.from_product(
        [pd.to_datetime(["2020-01-31", "2020-02-29"]), ["AAA", "BBB"]],
        names=["date", "ticker"],
    )
    score_frame = pd.DataFrame(
        {
            "volatility_score": [0.2, 0.8, 0.9, 0.1],
        },
        index=index,
    )
    provider = build_alpha_score_provider(score_frame)

    scores = provider(pd.Timestamp("2020-03-15"), ["AAA", "BBB"], object())

    assert list(scores.index) == ["AAA", "BBB"]
    assert scores["AAA"] == 0.9
    assert scores["BBB"] == 0.1
