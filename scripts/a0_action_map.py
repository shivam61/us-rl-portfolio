"""A0 task 1a: action -> realised exposure map for the 2-dim equity-only action [raw_equity, raw_cash].

Pure function of the action (no market data). Writes runs_a0/action_map_grid.csv and prints the
corner / degenerate table. Also provides raw_for_equity(target): the corrected inverse of the mapping
for a target equity share in [0.5, 1.0] (the old helper mis-inverted 0.5 < target < 2/3).

Usage: .venv/bin/python scripts/a0_action_map.py
"""
import csv
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.rl.exposure_mix import _CA_MAX, _CA_MIN, _EQ_MAX, _EQ_MIN, project_two_sleeve  # noqa: E402

OUT = REPO_ROOT / "runs_a0"


def equity_floor() -> float:
    """Smallest realised equity share reachable: cash is capped at _CA_MAX, so eq >= 1 - _CA_MAX."""
    return 1.0 - _CA_MAX


def raw_for_equity(target: float) -> tuple[float, float]:
    """Return (raw_eq, raw_ca) whose projection realises equity share `target`.

    Derivation: eq = eq_s / (eq_s + ca_s), cash = min(1 - eq, _CA_MAX).
      - target in [0.5, 2/3): cash is at the cap, ca_s = _CA_MAX, eq_s = _CA_MAX * t / (1 - t).
      - target in [2/3, 1]: eq_s = _EQ_MAX, ca_s = (1 - t) / t * eq_s.
    Raises ValueError outside [1 - _CA_MAX, 1].
    """
    t = float(target)
    lo = equity_floor()
    if t < lo - 1e-12 or t > 1.0 + 1e-12:
        raise ValueError(f"target equity {t} outside reachable [{lo}, 1.0]")
    t = min(max(t, lo), 1.0)
    if t < 2.0 / 3.0:
        eq_s = _CA_MAX * t / (1.0 - t) if t < 1.0 else _EQ_MAX
        ca_s = _CA_MAX
    else:
        eq_s = _EQ_MAX
        ca_s = eq_s * (1.0 - t) / t
    raw_eq = 2.0 * (eq_s - _EQ_MIN) / (_EQ_MAX - _EQ_MIN) - 1.0
    raw_ca = 2.0 * (ca_s - _CA_MIN) / (_CA_MAX - _CA_MIN) - 1.0
    return float(np.clip(raw_eq, -1.0, 1.0)), float(np.clip(raw_ca, -1.0, 1.0))


def write_grid(n: int = 21) -> list[dict]:
    rows = []
    grid = np.linspace(-1.0, 1.0, n)
    for re_ in grid:
        for rc in grid:
            eq, ca = project_two_sleeve(float(re_), float(rc))
            rows.append({"raw_eq": round(float(re_), 4), "raw_ca": round(float(rc), 4),
                         "equity": eq, "cash": ca, "sum": eq + ca,
                         "floor_binds": int(abs(eq - equity_floor()) < 1e-12),
                         "cash_cap_binds": int(abs(ca - _CA_MAX) < 1e-12)})
    OUT.mkdir(exist_ok=True)
    with open(OUT / "action_map_grid.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return rows


def main():
    rows = write_grid()
    n = len(rows)
    fl = sum(r["floor_binds"] for r in rows)
    print(f"grid points={n}; equity range [{min(r['equity'] for r in rows):.4f}, "
          f"{max(r['equity'] for r in rows):.4f}]; floor(0.5) binds on {fl}/{n} points "
          f"({100 * fl / n:.1f}%) on the uniform raw grid")
    corners = [(-1, -1), (-1, 1), (1, -1), (1, 1), (0, 0)]
    print("corner / centre cases:")
    for re_, rc in corners:
        eq, ca = project_two_sleeve(re_, rc)
        print(f"  raw=({re_:+.0f},{rc:+.0f}) -> equity={eq:.4f} cash={ca:.4f}")
    for t in (0.5, 0.55, 0.6, 0.612, 2 / 3, 0.75, 0.9, 1.0):
        re_, rc = raw_for_equity(t)
        eq, ca = project_two_sleeve(re_, rc)
        print(f"  target={t:.4f} raw=({re_:+.4f},{rc:+.4f}) realised={eq:.9f} err={eq - t:+.2e}")


if __name__ == "__main__":
    main()
