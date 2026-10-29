# Spacing proof for 1.300

The spacing revision reduces the white pocket after the upright **l**. The shorter foot allows a narrower advance without crowding its tip.

## Research informed the tests

[Glyphs spacing guidance](https://glyphsapp.com/learn/spacing) recommends comparing straight and rounded forms at the intended size before adding kerning.

[FontForge metrics guidance](https://fontforge.org/docs/tutorial/editexample5) recommends judging letters in context. Pair adjustments handle combinations that default spacing cannot resolve.

[Typotheque on optical spacing](https://www.typotheque.com/articles/size-specific-spacing-of-fonts) explains why a spacing choice can work differently at small and large sizes.

Those methods informed a custom corpus of **229 distinct words, phrases, and control strings**. The sources do not certify this font or supply that word list.

## Test the difficult combinations

| Group | Examples |
|---|---|
| Requested words | Miracles, gentle, little, welcome |
| Rounded neighbors | clear, circle, close, local, older, school, welcome |
| Repeated stems | lily, lullaby, minimum, million, inner, modern |
| Tall neighbors | gently, shelter, helpful, filter, wildlife, children |
| Ligatures | fluffy, flowers, offline, affliction, waffle, shuffle, truffle |
| Diagonals and capitals | AVATAR, WAVE, VAND, Today, Together, Youth |
| Accents | élève, clé, cálculo, círculo, fáciles, łagodny |
| Control strings | noononno, HOOHHOHO, lelele, clclcl, liliilil |

Browse [the complete corpus](../qa/spacing-corpus.json). It includes punctuation and complete sentences as well as individual words.

## Results and scope

Testing ran on **2026-10-28**, using HarfBuzz and FreeType on Windows. [The saved results](../qa/spacing-results.json) record the tested styles and sizes.

| Check | Result |
|---|---|
| Styles | All 8 styles |
| Raster sizes | 16, 24, 36, 48, 72, and 112 pixels |
| Shaping cases | 7,328 passed |
| Feature modes | Default, kerning off, ligatures off, expressive alternates |
| Accent normalization | Composed and decomposed strings matched in all shaping cases |
| Default raster comparisons | 10,992 comparisons against 1.200 |
| Increased neighboring-glyph overlap | None detected at the chosen threshold |
| Focused spacing regressions | 44 cases across 4 upright weights |
| Alphabet-neighbor check | 416 cases, with no new bounding-box collisions |

The raster comparison checks adjacent glyph masks at an opacity threshold of **160/255**. It measures overlap, not perceived spacing or reading speed.

It uses unhinted FreeType rendering, rounded glyph origins, and the default feature settings. Existing contacts are compared with the earlier version rather than treated as new failures.

Visual review covered the requested words in all 8 styles at all 6 sizes. Additional corpus sheets were reviewed at 36 pixels in representative upright and italic styles.

The revised **l** improves the rhythm in these samples. The proofs did not reveal a reason to tighten their other pairs further.

At 16 pixels, Bold and Bold Italic remain visually dense. Regular and Medium provide more open counters for small text in these proofs.

This is a display-oriented family with a fixed optical size. The study does not establish readability for every reader, device, application, or language.

## Repeat the study

Open [the interactive spacing proof](../spacing-proof.html) to compare weights and feature settings. Its samples use font spacing without logo-specific positioning.

Install **requirements-proof.txt**, then extract the 1.200 release as the baseline. Run the following command with its TTF directory:

```sh
python scripts/spacing_study.py --baseline /path/to/1.200/ttf
```

Results include PNG proofs and a JSON report under **build/spacing-study**. Keep the renderer version consistent when comparing raster results.

Outlined Animal Miracles artwork includes separate optical adjustments. Those positions belong to the logo and are not applied to ordinary text.
