"""
Summary statistics shared by the figures.

RT, ET and MD are right-skewed with occasional very slow or very messy trials, and a
per-block point rests on only ~5 trials, so learning curves summarise them by the
median. Its error bar is a bootstrap interval rather than an SEM, which describes a mean.
"""

import numpy as np


def median_ci(v, rng, n_boot=2000, level=.68):
    """Median of v and a bootstrap CI, returned as (median, (below, above)).

    `below` / `above` are distances from the median, ready for errorbar(yerr=...).
    level=.68 makes the bars the median's analogue of +/-1 SEM.
    """
    v = np.asarray(v, dtype=float)
    m = np.median(v)
    if len(v) < 2:
        return m, (0.0, 0.0)
    boot = np.median(rng.choice(v, size=(n_boot, len(v))), axis=1)
    lo, hi = np.percentile(boot, [50 * (1 - level), 50 * (1 + level)])
    return m, (max(m - lo, 0.0), max(hi - m, 0.0))
