"""
The shared x-axis of every learning-curve figure.

All blocks of the full design (utils/design.py) run left to right, one slot per block,
with a gap at every phase and a wider one at every day boundary. The layout is the same
for every subject, so figures line up across subjects; blocks without data are hatched.

With `pool_tests=True`, Test 1 and Test 2 each collapse to a single 2-unit slot so each
chord can be drawn as one point per test.

Typical use:

    segs = layout(pool_tests)
    draw_background(ax, segs, collected)
    ...plot, using seg["x"][block] or seg["center"] for pooled segments...
    ax.set_ylim(...)
    draw_axis(ax, segs)                      # ticks + day / segment headers
"""

from utils.design import LAST_BLOCK, SEGMENTS

POOLED_SEGMENTS = {"Test 1", "Test 2"}
PHASE_GAP, DAY_GAP = 1.1, 2.4

_HATCH = dict(facecolor="none", edgecolor="0.75", hatch="///", linewidth=0,
              zorder=.5, alpha=.55)


def layout(pool_tests=False):
    """Place the segments along x. Returns copies of SEGMENTS with positions added.

    Per-block segment: seg["x"] = {block: x}. Pooled segment: seg["center"].
    Every segment: seg["span"] = (lo, hi), seg["pooled"] = bool.
    """
    segs = [dict(s, pooled=pool_tests and s["name"] in POOLED_SEGMENTS) for s in SEGMENTS]
    cursor = 0.0
    for i, seg in enumerate(segs):
        if i:
            cursor += 1.0 + (DAY_GAP if seg["day"] != segs[i - 1]["day"] else PHASE_GAP)
        if seg["pooled"]:
            seg["center"] = cursor + 1.0
            seg["span"] = (cursor - 0.35, cursor + 2.35)
            cursor += 2.0
        else:
            seg["x"] = {b: cursor + k for k, b in enumerate(seg["blocks"])}
            seg["span"] = (cursor - 0.5, cursor + len(seg["blocks"]) - 0.5)
            cursor += len(seg["blocks"]) - 1.0
    return segs


def draw_background(ax, segs, collected):
    """Grey behind the 4-finger segments, hatching over blocks without data."""
    for seg in segs:
        if seg["kind"] == "4f":
            ax.axvspan(*seg["span"], color="0.94", zorder=0)
        if seg["pooled"]:
            if not set(seg["blocks"]) & collected:
                ax.axvspan(*seg["span"], **_HATCH)
            continue
        for b in seg["blocks"]:
            if b not in collected:
                ax.axvspan(seg["x"][b] - .5, seg["x"][b] + .5, **_HATCH)


def draw_axis(ax, segs, headers=True):
    """Block ticks, x limits and, above the axes, the day and segment headers.

    Call after the y limits are final: the headers are placed relative to them.
    """
    ticks, labels = [], []
    for seg in segs:
        if seg["pooled"]:
            ticks.append(seg["center"])
            labels.append(f"blocks\n{min(seg['blocks'])}–{max(seg['blocks'])}")
            continue
        for b in seg["blocks"]:
            if b % 2:
                ticks.append(seg["x"][b]); labels.append(str(b))
    ax.set_xticks(ticks); ax.set_xticklabels(labels, fontsize=8.5)
    ax.set_xlim(segs[0]["span"][0] - .6, segs[-1]["span"][1] + .6)
    if not headers:
        return

    y0, y1 = ax.get_ylim()
    top = y1 + (y1 - y0) * .10
    for day in sorted({s["day"] for s in segs}):
        day_segs = [s for s in segs if s["day"] == day]
        lo = min(s["span"][0] for s in day_segs); hi = max(s["span"][1] for s in day_segs)
        ax.plot([lo, hi], [top, top], color="0.25", lw=1.2, clip_on=False, zorder=5)
        ax.text((lo + hi) / 2, top + (y1 - y0) * .022, f"Day {day}", ha="center", va="bottom",
                fontsize=10.5, fontweight="bold", color="0.2", clip_on=False)
    for seg in segs:
        lo, hi = seg["span"]
        if seg["kind"] == "2f":
            txt = "Training (2-finger components)"
        elif hi - lo <= 4.5 and len(seg["name"]) > 8:
            txt = seg["name"].replace(" ", "\n", 1)     # narrow segment: stack the words
        else:
            txt = seg["name"]
        ax.text((lo + hi) / 2, y1 + (y1 - y0) * .012, txt, ha="center", va="bottom",
                fontsize=8.8, style="italic", color="0.45", clip_on=False, linespacing=1.05)


def missing_note(sn, collected):
    """Footnote text explaining the hatching, or '' if nothing is hatched."""
    all_blocks = sorted(b for s in SEGMENTS for b in s["blocks"])
    not_in_design = [b for b in all_blocks if sn in LAST_BLOCK and b > LAST_BLOCK[sn]]
    pending = [b for b in all_blocks if b not in collected and b not in not_in_design]
    note = ""
    if not_in_design:
        note += f"   Hatched = blocks {_runs(not_in_design)} not part of s{sn}'s design."
    if pending:
        note += f"   Hatched = blocks {_runs(pending)} not yet collected."
    return note


def _runs(blocks):
    """[1, 2, 3, 7] -> '1–3, 7'"""
    out, start = [], None
    for i, b in enumerate(blocks):
        if start is None:
            start = b
        if i + 1 == len(blocks) or blocks[i + 1] != b + 1:
            out.append(f"{start}–{b}" if b != start else str(b))
            start = None
    return ", ".join(out)
