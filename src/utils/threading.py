"""
Thread budget calculator for joblib + LightGBM parallelism.

Rule: joblib_jobs × lgbm_threads <= total_cpus

Tuning guidance:
  - Small data (<50K rows, e.g. sp100): maximize outer jobs, lgbm saturates at 2 threads
  - Large data (>200K rows, e.g. sp500): fewer outer jobs, lgbm scales to 8+ threads
  - Phase B/C grid search: balanced (8 × 4)
"""
import os

TOTAL_CPUS: int = os.cpu_count() or 32


def compute_thread_budget(
    n_outer_jobs: int,
    total_cpus: int = TOTAL_CPUS,
    min_lgbm_threads: int = 1,
) -> tuple[int, int]:
    """
    Returns (joblib_jobs, lgbm_threads) with product <= total_cpus.

    Prefers more outer jobs (maximises parallelism across independent tasks)
    and assigns remaining cores to LightGBM.
    """
    actual_jobs = min(n_outer_jobs, total_cpus)
    lgbm_threads = max(min_lgbm_threads, total_cpus // actual_jobs)
    return actual_jobs, lgbm_threads


def set_thread_env(n_threads: int) -> None:
    """
    Set all relevant thread-count env vars.
    Must be called before importing numpy / lightgbm in worker processes.
    Safe to call in the parent — loky workers inherit env vars on spawn.
    """
    for var in (
        "OMP_NUM_THREADS",
        "MKL_NUM_THREADS",
        "OPENBLAS_NUM_THREADS",
        "NUMEXPR_NUM_THREADS",
    ):
        os.environ[var] = str(n_threads)
    os.environ["LGBM_N_JOBS"] = str(n_threads)
