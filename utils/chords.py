"""
Chord roles and their plotting style, shared by every figure.

Nothing is hard-coded to one counterbalancing group: the trained components are
whatever chords a subject practised in the training blocks, and each 4-finger chord is
scored by which of those components are embedded in it.
"""

FINGERS = ["thumb", "index", "middle", "ring", "pinky"]

# role of a 4-finger chord -> (label, colour, marker); ordered both, 1st, 2nd, neither
_TESTED_STYLE = {
    0: ("both components trained", "#0173B2", "o"),
    1: ("1st component trained", "#56B4E9", "s"),
    2: ("2nd component trained", "#009E73", "^"),
    3: ("neither component trained", "#949494", "D"),
}
_TRAINED_STYLE = [("1st", "#E69F00", "o"), ("2nd", "#CC79A7", "s")]


class ChordRoles:
    """Which component each chord contains, plus a consistent label/colour/marker.

    Parameters
    ----------
    trained : chords practised in the training blocks (the 2-finger components)
    tested : the 4-finger chords
    """

    def __init__(self, trained, tested):
        # each component occupies a fixed pair of finger slots (9 = relaxed)
        self.component = {self.slot_of(c): int(c) for c in trained}
        self.slots = sorted(self.component)                  # 1st, 2nd
        self.trained = [self.component[s] for s in self.slots]
        self.tested = sorted((int(c) for c in tested), key=self.role)

        self.label, self.color, self.marker = {}, {}, {}
        for c in self.tested:
            text, self.color[c], self.marker[c] = _TESTED_STYLE[self.role(c)]
            self.label[c] = f"{c}  {text}"
        for c, (which, col, mk) in zip(self.trained, _TRAINED_STYLE):
            self.label[c] = f"{c}  trained component ({which})"
            self.color[c], self.marker[c] = col, mk

    @staticmethod
    def slot_of(chord):
        """Finger indices a chord moves: 12999 -> (0, 1)."""
        return tuple(i for i, d in enumerate(str(chord)) if d != "9")

    def contains(self, chord, slot):
        """True if `chord` makes the trained component that lives at `slot`."""
        comp = str(self.component[slot])
        return all(str(chord)[i] == comp[i] for i in slot)

    def role(self, chord):
        """0 both, 1 first only, 2 second only, 3 neither component embedded."""
        first, second = (self.contains(chord, s) for s in self.slots)
        return {(True, True): 0, (True, False): 1, (False, True): 2, (False, False): 3}[
            (first, second)]

    def slot_name(self, slot):
        return "+".join(FINGERS[i] for i in slot)
