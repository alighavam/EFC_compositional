"""
Session structure of EFC_compositional: the one place block numbers are defined.

Every subject runs the same numbered blocks (the layout in makeTGT.ipynb):

    day 1   1-4    Test 1               4-finger chords, before any training
            5-14   Training             2-finger components
    day 2   15-24  Training             2-finger components
    day 3   25-34  Training             2-finger components
            35-38  Test 2               4-finger chords, after component training
            39-42  4-finger training    the same 4-finger chords, practised
    day 4   43-52  4-finger training    the same 4-finger chords, practised

s100 was the pilot. It ran the same blocks up to Test 2 and stopped at block 38, so
blocks 39-52 do not exist for that subject. Figures still draw the full layout for
every subject, so s100 lines up with everyone else and just leaves those blocks empty.

`kind` says which chords a segment contains: "4f" = the tested 4-finger chords,
"2f" = the trained 2-finger components.
"""

SEGMENTS = [
    dict(name="Test 1",            day=1, blocks=range(1, 5),   kind="4f"),
    dict(name="Training",          day=1, blocks=range(5, 15),  kind="2f"),
    dict(name="Training",          day=2, blocks=range(15, 25), kind="2f"),
    dict(name="Training",          day=3, blocks=range(25, 35), kind="2f"),
    dict(name="Test 2",            day=3, blocks=range(35, 39), kind="4f"),
    dict(name="4-finger training", day=3, blocks=range(39, 43), kind="4f"),
    dict(name="4-finger training", day=4, blocks=range(43, 53), kind="4f"),
]

# subjects whose design ends early: sn -> last block they were ever meant to run
LAST_BLOCK = {100: 38}

# named block sets used across the analysis notebooks
TEST1_BLOCKS = range(1, 5)            # day 1, before training
TEST2_BLOCKS = range(35, 39)          # day 3, right after component training
TRAIN_BLOCKS = range(5, 35)           # all 2-finger component training
TRAIN_EARLY = [5, 6, 7, 8]            # first four component blocks, day 1
TRAIN_LATE = [31, 32, 33, 34]         # last four component blocks, day 3


def segments(sn):
    """The segments of the full layout that are part of this subject's design."""
    last = LAST_BLOCK.get(sn)
    return [s for s in SEGMENTS if last is None or max(s["blocks"]) <= last]


def day_blocks(sn):
    """{day: [block numbers]} for this subject's design."""
    out = {}
    for s in segments(sn):
        out.setdefault(s["day"], []).extend(s["blocks"])
    return out


def day_of_block(sn):
    """{block number: day} for this subject's design."""
    return {b: d for d, blocks in day_blocks(sn).items() for b in blocks}
