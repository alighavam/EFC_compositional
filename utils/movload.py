"""
Loading of .mov files.

The .mov layout is *detected from the file* rather than hard-coded. The C++ task
writes four trailing blocks of five force columns, always in this order:

    extension | flexion | differential | visualized

preceded by a handful of metadata columns. The force blocks are therefore
anchored to the right-hand edge of the row and whatever is left in front of them
is metadata, which is what makes the reader portable across task versions.

EFC_compositional writes 24 columns:

    0  trialNum   1  state   2  timeReal   3  time
    4-8    extension force        9-13   flexion force
    14-18  differential force     19-23  visualized force

EFC2 wrote 23 - the same layout without the leading trialNum - which is why
fixed column indices copied from that project silently read the wrong columns
here (state <- trialNum, differential force <- flexion force).

Two things worth remembering about the differential force:

* it is RAW. The task computes it as `ext - flex` with no gains applied, so to
  recover what the subject actually saw you must multiply by the global
  forceGain and the per-finger fGain, both of which are recorded per trial in
  the .dat.
* `visualized force` is the same signal with those gains already applied, so
  `vis == forceGain * fGain * diff` is a useful invariant to assert against.
"""

import numpy as np

N_FINGERS = 5
FORCE_BLOCKS = ("ext", "flex", "diff", "vis")      # order the task writes them
META_BY_COUNT = {
    4: ("trialNum", "state", "timeReal", "time"),  # EFC_compositional
    3: ("state", "timeReal", "time"),              # EFC2 and older tasks
}


def movload(fname):
    """Load a .mov file and detect its column layout.

    Parameters
    ----------
    fname : str or Path
        Path to the .mov file.

    Returns
    -------
    trials : list of ndarray
        One (n_samples, n_cols) float array per trial, in file order.
    cols : dict
        Column lookup. Metadata names map to a single index, force block names
        map to a list of five indices, so a block is read as
        ``trial[:, cols["diff"]]``.

    Raises
    ------
    ValueError
        If the row width does not correspond to a known layout, or if the trial
        headers are malformed.
    """
    trials, current, n_cols = [], None, None

    with open(fname, "rt") as fid:
        for lineno, line in enumerate(fid, start=1):
            line = line.rstrip("\n")
            if not line.strip():
                continue

            if line.startswith("T"):                    # "Trial <n>" header
                parts = line.split()
                if len(parts) < 2:
                    raise ValueError(f"{fname}:{lineno}: malformed trial header {line!r}")
                expected = len(trials) + 1
                if int(parts[1]) != expected:
                    print(f"  warning: {fname} trial header {parts[1]} out of "
                          f"sequence (expected {expected})")
                current = []
                trials.append(current)
                continue

            if current is None:
                raise ValueError(f"{fname}:{lineno}: data row before any trial header")

            # rows carry a trailing tab, which would otherwise parse as an empty field
            values = [float(x) for x in line.rstrip("\t").split("\t")]
            if n_cols is None:
                n_cols = len(values)
            elif len(values) != n_cols:
                raise ValueError(f"{fname}:{lineno}: row has {len(values)} columns, "
                                 f"expected {n_cols}")
            current.append(values)

    if n_cols is None:
        raise ValueError(f"{fname}: no data rows found")

    cols = _detect_columns(n_cols, fname)
    trials = [np.asarray(t, dtype=float) for t in trials]
    return trials, cols


def _detect_columns(n_cols, fname=""):
    """Map column names to indices by anchoring the force blocks to the right edge."""
    n_meta = n_cols - N_FINGERS * len(FORCE_BLOCKS)
    if n_meta < 1:
        raise ValueError(f"{fname}: {n_cols} columns is too few for "
                         f"{len(FORCE_BLOCKS)} blocks of {N_FINGERS} forces")

    if n_meta in META_BY_COUNT:
        meta = META_BY_COUNT[n_meta]
    else:
        meta = tuple(f"meta{i}" for i in range(n_meta))
        print(f"  warning: {fname} has {n_meta} unrecognised metadata columns; "
              f"named {meta[0]}..{meta[-1]}. Add this layout to META_BY_COUNT.")

    cols = {name: i for i, name in enumerate(meta)}
    for b, name in enumerate(FORCE_BLOCKS):
        start = n_meta + b * N_FINGERS
        cols[name] = list(range(start, start + N_FINGERS))
    return cols
