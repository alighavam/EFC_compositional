"""
Movement onset and acquisition, detected with the task's rules (EFC_compositional.cpp,
WAIT_EXEC) but for any subset of fingers.

The task works on the gain-applied, *unsmoothed* force (`force_raw` in the .pkl):

* a finger has left the baseline zone when |F| >= baselineTopThresh;
* a finger is in its zone when   ext  (1): extBotThresh  <= F <= extTopThresh
                                 flex (2): flexTopThresh <= F <= flexBotThresh
                                 relaxed (9): |F| <= baselineTopThresh
* RT      = first execution-phase sample where ANY finger has left the baseline zone;
* RT + ET = onset of the last all-fingers-correct period, i.e. the start of the hold
            that succeeded (ET is overwritten at every new acquisition).

`first_approach` adds one event the task does not record: the first time a set of
fingers reaches its target configuration (and holds it briefly), before any later drift
out of the zones and re-acquisition.

Threshold ties. The .mov stores force to 3 decimals, so a recorded 1.200 may have been
1.1996 (below the baseline threshold) or 1.2004 (above it) when the task tested it. A
recorded value exactly on a threshold is therefore ambiguous, and here it counts as
*neither* side: a threshold is only met when the recorded value is strictly past it.
With that rule, the detector run on all five fingers gives the task's RT + ET on every
trial and its RT on ~99% (the rest within 6 ms, i.e. 3 samples), which is how it is
validated in component_md.ipynb.
"""

import numpy as np

WAIT_EXEC = 3


def in_zone(F, digit, tr):
    """Boolean mask: is force trace F unambiguously inside the zone the digit asks for?"""
    if digit == "1":
        return (F > tr.extBotThresh) & (F < tr.extTopThresh)
    if digit == "2":
        return (F > tr.flexTopThresh) & (F < tr.flexBotThresh)
    return np.abs(F) < tr.baselineTopThresh


def movement_window(rec, tr, fingers):
    """(start, end) of the movement of `fingers`, in ms from the go cue.

    start : first execution sample where any of `fingers` has left the baseline zone.
    end   : onset of the period in which all of `fingers` are in their zones that is
            still ongoing when the whole chord was acquired (go cue + RT + ET). If a
            threshold tie leaves the fingers out of zone at that exact sample, the
            period that begins right after it is used. Never later than the chord's
            acquisition, since by the task's own check every finger was in zone then.

    `rec` needs `t`, `state` and `force_raw`; `tr` is the trial's row from s<sn>.csv
    (correct trials only). Returns NaN for an event that cannot be found.
    """
    ex = rec.state == WAIT_EXEC
    if not ex.any():
        return np.nan, np.nan
    t0 = rec.t[ex][0]
    F = rec.force_raw[:, list(fingers)]
    chord = str(int(tr.chordID))

    left = ex & (np.abs(F) > tr.baselineTopThresh).any(axis=1)
    start = rec.t[left][0] - t0 if left.any() else np.nan

    ok = ex.copy()
    for j, k in enumerate(fingers):
        ok &= in_zone(F[:, j], chord[k], tr)
    acq_t = tr.RT + tr.ET
    hit = np.flatnonzero(rec.t == t0 + acq_t)
    if len(hit) != 1:
        return start, np.nan
    after = np.flatnonzero(ok[hit[0]:])
    if not len(after):
        return start, np.nan
    i = hit[0] + after[0]
    while i > 0 and ok[i - 1]:
        i -= 1
    return start, min(rec.t[i] - t0, acq_t)


def first_approach(rec, tr, fingers, start, end, hold_ms=100):
    """When `fingers` first reach their target configuration, in ms from the go cue.

    `start`, `end` are the pair's movement window from `movement_window`. The first
    approach is the onset of the first period after `start` in which all of `fingers`
    are in their zones and that either lasts >= hold_ms or is the final hold (still
    ongoing at `end`). The hold requirement skips passing through a bounded zone on the
    way to overshooting it. Never later than `end`, since the final hold always
    qualifies; equal to `end` when the pair got there in one go.

    Same zone rule and signal (`force_raw`) as `movement_window`. Returns NaN if `end`
    is NaN.
    """
    if not np.isfinite(end):
        return np.nan
    ex = rec.state == WAIT_EXEC
    t = rec.t - rec.t[ex][0]
    chord = str(int(tr.chordID))
    ok = ex & (t >= start)
    for k in fingers:
        ok &= in_zone(rec.force_raw[:, k], chord[k], tr)
    dt = np.median(np.diff(rec.t))
    edges = np.diff(np.r_[0, ok.astype(int), 0])
    for a, b in zip(np.flatnonzero(edges == 1), np.flatnonzero(edges == -1)):
        if t[a] >= end:
            break
        if t[b - 1] - t[a] + dt >= hold_ms or t[b - 1] >= end:
            return t[a]
    return end
