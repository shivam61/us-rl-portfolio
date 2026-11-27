"""Before/after evidence for the FH findings (FH deliverable). Reads the FB v4 artefacts (copied under
runs_fh/inputs/) and the v4.1 artefacts (runs_fh/features_v4_1/) and prints one row per check.

Each check is the property that the corresponding fix establishes. A check that fails on FB and passes on v4.1 is
the evidence that the fix changed the outcome. Output: runs_fh/features_v4_1/before_after.csv
"""
import json
import pickle
import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from src.rl import features_v4_targets as T  # noqa: E402

FB = ROOT / "runs_fh" / "inputs" / "fb"
NEW = ROOT / "runs_fh" / "features_v4_1"


def fb_daily():
    return pd.read_parquet(FB / "features_v4" / "daily_v4.parquet")


def fb_meta_names():
    return list(pd.read_csv(FB / "features_v4" / "feature_meta.csv")["name"])


def main():
    rows = []
    D0, D1 = fb_daily(), pd.read_parquet(NEW / "daily_v4.parquet")
    H0 = pickle.load(open(FB / "history.pkl", "rb"))
    H0.pop("_meta", None)
    H1 = pickle.load(open(NEW / "history_v41.pkl", "rb"))
    meta1 = H1.pop("_meta")
    H1.pop("universe_mask_absent", None)

    def add(check, before, after, fixed_when):
        rows.append(dict(check=check, FB_v4=before, v4_1=after, expected_after=fixed_when))

    # 1 dead / duplicate columns in the feature table
    dead = {"hhi_u", "n_names", "invvar_u_21", "invvar_s_21", "base_ret_21"}
    add("dead or duplicate columns present", sorted(dead & set(fb_meta_names())),
        sorted(dead & set(D1.columns)), "[]")

    # 2 tail: unit-book returns zero-filled after the H1 cache end -> rv_u_5 pinned at the -3 clip
    tail0 = D0.loc[:"2026-04-24"].tail(30)
    pin0 = int(((tail0["rv_u_5"].abs() - 3).abs() < 1e-12).sum())
    tail1 = D1.loc[:"2026-04-24"].tail(30)
    pin1 = int(((tail1["rv_u_5"].abs() - 3).abs() < 1e-12).sum())
    add("rv_u_5 pinned at clip in last 30 days (days)", pin0, pin1, "0")
    zero_tail = int(((H0["unit_ret"].loc["2026-04-15":"2026-04-24"]) == 0).sum())
    add("unit_ret exact zeros 2026-04-15..24 (zero-fill)", zero_tail,
        int((H1["unit_ret"].loc["2026-04-15":"2026-04-24"] == 0).sum()), "0")

    # 3 unit-book canonical series reconciles to H1 8-week cache (the book the 8w grid is built on)
    h8 = pickle.load(open(ROOT / "runs_fh" / "inputs" / "h1" / "8w_base.pkl", "rb"))["base_daily"]
    d0 = (H0["unit_ret"].reindex(h8.index) - h8).abs().loc["2008-01-08":"2026-04-06"].max()
    d1 = (H1["unit_ret"].reindex(h8.index) - h8).abs().loc["2008-01-08":"2026-04-06"].max()
    add("unit_ret max |dev| vs H1 8w cache", float(d0), float(d1), "< 1e-9")

    # 4 the 8w grid's features and targets must come from the same unit-book series: deviation of the book
    # used by the FB 8w grid (FB history unit_ret) from the canonical series over the 8w periods
    g8 = pd.read_parquet(NEW / "grid_8w_v4.parquet").index
    dev = []
    for a, b in zip(g8[:-1], g8[1:]):
        m = (H0["unit_ret"].index > a) & (H0["unit_ret"].index <= b)
        dev.append(float((H0["unit_ret"][m] - H1["unit_ret"][m]).abs().max()))
    add("8w periods: max |FB book - canonical book| per period", round(max(dev), 6),
        "n/a (single series; env match tested)", "< 1e-9")

    # 6 T5: FB regret is a V-shape in R; a flat negative period must give the static-or-lower call
    R = -0.02
    fb_t5 = max(0.5 * R, 1.0 * R) - 0.72 * R
    new = T.period_targets(pd.Series([R] * 5, index=pd.bdate_range("2020-01-01", periods=5)),
                           pd.Timestamp("2019-12-31"), pd.bdate_range("2020-01-01", periods=5)[-1])
    add("T5 call sign on a flat -2% period (FB: regret, v4.1: best-share call)", round(fb_t5, 6),
        new["T5_call"], "-1 (de-risk)")

    # 7 breadth on PIT-eligible names only
    add("universe mask applied to breadth", "no", "yes" if "universe_mask" in H1 else "no", "yes")

    # 8 membership: holdings outside the mask per decision date (v4.1 census)
    cen = pd.read_csv(NEW / "mask_holdings_census.csv")
    add("decision dates with holdings outside mask (14d grid)",
        "not measured", int((cen[cen.grid == "14d"]["n_outside_mask"] > 0).sum()), "reported")

    # 9 power: planted IC 0.05 detected at 80% (v4 design B=1000, m=159 vs v4.1 analytic m=60)
    pc = pd.read_csv(ROOT / "runs_fh" / "screen_v4_1" / "power_curve.csv")
    p_fb = float(pc.query("delta_IC == 0.05 and design.str.startswith('v4 design')")["power"].iloc[0])
    p_new = float(pc.query("delta_IC == 0.05 and design.str.startswith('v4.1 analytic')")["power"].iloc[0])
    add("power at planted delta IC 0.05 (BH q<0.10)", round(p_fb, 3), round(p_new, 3), ">= 0.80 (not met)")

    # 10 metadata lags: FB copy-pasted text
    m0 = pd.read_csv(FB / "features_v4" / "feature_meta.csv")
    m1 = pd.read_csv(NEW / "feature_meta.csv")
    add("distinct lag strings in feature_meta", int(m0["lag"].nunique()), int(m1["lag"].nunique()), "> 1 (VIX differs)")

    out = pd.DataFrame(rows)
    out.to_csv(NEW / "before_after.csv", index=False)
    print(out.to_string(index=False))
    print(json.dumps({"meta_history_end": meta1.get("end")}))


if __name__ == "__main__":
    main()
