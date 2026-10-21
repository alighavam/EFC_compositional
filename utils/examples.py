"""
Picking and labelling the example trials drawn by arrival_gap.ipynb and velocity.ipynb.

Correct trials are always preferred. When a session has fewer correct trials of a chord
than the figure has rows (in the extreme, none at all: s102 and s103 never produced the
ring+pinky chords in Test 1), the remaining rows are filled with unsuccessful trials, so
the session is shown rather than left blank. Those panels are tinted and tagged, so they
cannot be mistaken for correct trials.

Plan errors are never used to fill in: the subject moved during planning, so the trial
failed for a reason unrelated to the chord.
"""

FAIL_COLOR = "#c0392b"
FAIL_FACE = "#fdf0ef"


def _spread(p, n, rng):
    """n random rows of p, spread as evenly as possible across its blocks.

    Sampling uniformly over a pooled session can land most of the draw in one block, and
    blocks differ several-fold in speed, so such a draw misrepresents the session. Here
    each block gets a quota, allocated one slot at a time to whichever block currently has
    the fewest (ties broken at random), and blocks that run out are skipped.
    """
    if p.empty or n <= 0:
        return []
    n = min(n, len(p))
    by_block = {int(b): g.index.to_numpy() for b, g in p.groupby("BN")}
    order = sorted(by_block)

    quota = {b: 0 for b in order}
    for _ in range(n):
        avail = [b for b in order if quota[b] < len(by_block[b])]
        if not avail:
            break
        fewest = min(quota[b] for b in avail)
        tied = [b for b in avail if quota[b] == fewest]
        quota[tied[rng.integers(len(tied))]] += 1

    picked = []
    for b in order:
        if quota[b]:
            picked += list(rng.choice(by_block[b], quota[b], replace=False))
    return [p.loc[i] for i in picked]


def sample(df, chord, blocks, n, rng):
    """Up to n example trials of `chord` from `blocks`, sorted by (BN, TN).

    Correct trials first; if there are fewer than n, unsuccessful (non-plan-error) trials
    fill the rest. The random draw for the correct trials is unchanged from before
    unsuccessful trials were added, so sessions with enough correct trials pick the
    same trials as they always did for a given seed.
    """
    pool = df[(df.chordID == chord) & df.BN.isin(blocks)]
    rows = _spread(pool[pool.trialPoint == 1], n, rng)
    if len(rows) < n:
        failed = pool[(pool.trialPoint == 0) & (pool.planError == 0)]
        rows += _spread(failed, n - len(rows), rng)
    return sorted(rows, key=lambda r: (r.BN, r.TN))


def outcome(tr):
    """How an unsuccessful trial failed, in a few words ('' for a correct trial)."""
    if tr.trialPoint == 1:
        return ""
    if tr.RT == 0:
        return "never moved"
    if tr.ET == 0:
        return f"never acquired in {tr.execMaxTime / 1000:.0f} s"
    return f"acquired, never held {tr.success_holdTime:.0f} ms"


def panel_title(tr):
    """'BN3 TN7    ET = 812 ms' for a correct trial; no ET for an unsuccessful one."""
    head = f"BN{int(tr.BN)} TN{int(tr.TN)}"
    return f"{head}    ET = {tr.ET:.0f} ms" if tr.trialPoint == 1 else f"{head}    ET —"


def mark_unsuccessful(ax, tr, fontsize=8.5):
    """Tint the panel and tag it in the top-right corner. No-op for a correct trial."""
    if tr.trialPoint == 1:
        return
    ax.set_facecolor(FAIL_FACE)
    ax.text(.995, .965, f"UNSUCCESSFUL · {outcome(tr)}", transform=ax.transAxes,
            ha="right", va="top", fontsize=fontsize, fontweight="bold", color="white",
            bbox=dict(boxstyle="round,pad=.28", fc=FAIL_COLOR, ec="none"), zorder=10)


def session_label(label, rows):
    """Append '[k of n unsuccessful]' to a session header when any shown trial failed."""
    k = sum(r.trialPoint != 1 for r in rows)
    return f"{label}   [{k} of {len(rows)} unsuccessful]" if k else label
