# How Miracle Grove differs from Fraunces

Miracle Grove is a modified Fraunces family. Its refinements began with the upright lowercase **l** and now extend to selected capitals, lowercase forms, and italics.

The alphabet, italics, and kerning largely come from Fraunces. This project does not claim that the full typeface was drawn from scratch.

## Fixed settings

| Setting | Value |
|---|---|
| Optical size | 36 |
| Softness | 100 |
| WONK axis | 0 |
| Regular source weight | 450, exposed as CSS weight 400 |
| Medium source weight | 550, exposed as CSS weight 500 |
| SemiBold source weight | 650, exposed as CSS weight 600 |
| Bold source weight | 750, exposed as CSS weight 700 |

The source weights give the family a little more presence. The fixed optical setting favors headings and short passages.

## Changed characters

The upright **l** retains the original upper stem and angled top. Its lower serif becomes a curved returning foot.

Composite accented forms inherit that foot during the build. The **fl** and **ffl** ligatures also use it.

The **lj** digraph needs more than a wider advance. Its **j** is moved to follow the wider **l** without crowding it.

The upright **ł** combines the new **l** with a crossing stroke. It should receive native-reader review before substantial Polish-language use.

## Refinements in 1.200

The approved Animal Miracles lettering informed the gently arched **A** bridge. Its midpoint is slightly thinner than its ends.

A shallower central valley softens **M**. The **h**, **m**, and **n** shoulders have a gentler lean.

Curved legs give **K** and **R** a restrained sweep. **Q** has a lifted tail, while **r** has a lighter terminal.

The crossbar of **e** has a shallow curve that echoes **A**. Existing advances and kerning remain in place.

The italic **l** replaces its hooked entrance with a softly angled cap. Slashed **ł** uses the revised stem and the inherited crossing stroke.

The italic **f** keeps its identifying hook with reduced terminal bulbs. Composite accents and standard ligatures inherit the changed outlines.

These italics remain based on Fraunces. The existing expressive alternates retain their earlier shapes and can differ from the revised default letters.

## Added behavior

Tabular figures place the existing numerals in the middle of equal advances. The digit shapes stay unchanged, and number columns become easier to align.

The `tnum` feature selects these numerals. The `pnum` feature restores proportional figures.

Ligature caret positions give compatible applications cursor stops within combined glyphs. Editing behavior still depends on the application.

The release also restores several existing Latin glyph mappings. It adds figure space, narrow nonbreaking space, and consistent U+2010 hyphen coverage.

## Production choices

Delivery fonts use decomposed outlines to avoid nested or transformed component issues. The build preserves the original family-wide vertical metrics.

No new hinting pass was added. Small-size rendering needs device testing rather than a promise based on a large specimen.

## Source attribution

Fraunces was designed by Phaedra Charles and Flavia Zimbardi of Undercase Type. Its copyright and license are preserved in this repository.

The vendored inputs come from the Google Fonts distribution. Their revision, source paths, and SHA-256 hashes appear in [the upstream lockfile](../upstream/lock.json).

You can explore the [Fraunces source repository](https://github.com/undercasetype/Fraunces). This derivative is not endorsed by the original designers.
