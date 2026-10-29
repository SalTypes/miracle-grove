# What has been tested

Release **1.300** passed FontBakery's Universal profile with **564 passes**, **0 failures**, and **0 errors** on Windows with Python 3.13.

The run also produced **40 warnings**, **298 skipped checks**, and **30 informational results**. A skipped check does not count as a pass.

## Read the remaining warnings

| Category | Meaning |
|---|---|
| Contour counts | Some outlines differ from the validator's typical contour-count assumptions. |
| Mathematical operator widths | Operators have different advances; this is not a mathematical typesetting font. |
| Soft hyphen | The inherited character remains; discretionary hyphenation needs application testing. |
| Unreachable glyphs | Some legacy forms remain unencoded and unused. Removing them is a future cleanup task. |
| Caron inspection | Decomposed outlines prevent the component-based check from judging these accent forms automatically. |

These warnings remain visible in [the audit output](../qa/fontbakery.txt). Native-reader review is still needed for less-tested Latin orthographies.

## Test shaped text

The regression suite checks all eight styles. It includes **64 sample-shaping runs** and **32 comparisons** between composed and decomposed accented text.

The samples cover Spanish accents, ligatures, and punctuation. They also include representative letters from several other Latin languages.

The suite checks equal advances for tabular digits and verifies that kerning changes the spacing of **AV**. It tests that `ffi` forms a ligature.

Desktop and web files must have equivalent character maps and core font tables. Font names must be unique, and line metrics must agree across styles.

Two local builds produced byte-identical font files. The repository's CI repeats this test on Windows and Linux; check the current workflow result for its status.

## Check revised spacing

Release 1.300 adds 44 spacing cases across the 4 upright weights. They check kerning for plain and accented l forms, plus fl and ffl ligatures.

The outgoing cases also require positive bounding-box clearance between neighboring outlines. This catches overlap in those samples; visual proofs remain necessary.

The expanded study covers 229 distinct entries at 6 sizes in all 8 styles. [The spacing report](spacing.md) records its methods and limits.

## Check browser behavior

For release **1.100**, the fonts loaded in Microsoft Edge on Windows. That earlier test specimen passed horizontal-overflow checks at **320**, **768**, and **1440 pixels**.

Each width was tested with ordinary spacing and expanded text spacing. The test used **48px** font samples and loaded all eight styles.

Those results do not certify the current specimen's entire accessibility or every browser. Safari, Firefox, and physical mobile-device tests remain open.

## Know the coverage limits

The family contains **639 encoded characters** per style. Character presence alone does not establish complete language support or good accent placement.

There is no dedicated `mark`/`mkmk` positioning system. Tested common accents work through normalization and precomposed glyphs; arbitrary stacked marks remain a limitation.

The fonts do not include small caps, arbitrary fractions, or non-Latin script families. They use a fixed optical setting and have no new hinting pass.

Application installation, editing behavior, PDF exports, and physical print proofs remain separate tests. Report the exact version and environment when contributing results.

## Methods and references

- [FontBakery Universal profile](https://fontbakery.readthedocs.io/en/stable/fontbakery/profiles/universal.html) explains the independent checks.
- [HarfBuzz shaping operations](https://harfbuzz.github.io/shaping-operations.html) describes substitutions and positioning.
- [Google Fonts metric guidance](https://googlefonts.github.io/gf-guide/metrics.html) informed the line-metric review.
- [OpenType naming specification](https://learn.microsoft.com/en-us/typography/opentype/spec/name) informed style metadata.
- [W3C text-spacing guidance](https://www.w3.org/WAI/WCAG22/Understanding/text-spacing) informed the browser spacing cases.
