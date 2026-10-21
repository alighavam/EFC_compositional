# TODO

All work goes in `notebooks/` as Jupyter notebooks.

## Pipeline
- [x] Preprocessing pipeline: raw `.dat` + `.mov` → tidy dataframes
- [x] Compute mean deviation (MD) from the `.mov` force traces

## Figures
- [ ] RT, ET, MD, success rate across blocks (days separated)
- [ ] Smoothed force patterns: 4-finger chords, before vs after learning
- [ ] Smoothed force patterns: 2-finger components during training (a few sample trials)

## Analysis — Test 2
- [ ] Order the 4 chords by condition: both / 1st only / 2nd only / neither components trained
- [ ] Test prediction: sharing the *easy* component (thumb+index) gives less generalization than sharing the *hard* one (ring+pinky)
- [ ] Locate Test 2 ET against the three models: parallel `max(c1,c2)`, sequential `c1+c2`, or non-compositional (Test 1 level)
- [ ] Do the components fuse, run sequentially, or neither? Look for a seam at the {1,2}/{4,5} trained boundary
