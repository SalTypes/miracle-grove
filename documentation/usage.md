# Install and use Miracle Grove

Extract the release ZIP before installing the fonts. The desktop files are in `ttf`; the web files are in `web`.

## Desktop installation

On Windows, select the eight TTF files, right-click, and choose **Install**. Some versions place that command under **Show more options**.

On macOS, open the TTF files in Font Book and install them. Restart applications that were open during installation.

On Linux, install them through your desktop font manager or place them in your user font directory. Refresh the font cache if needed.

These are standard installation procedures. This release has not been tested in every operating system's font manager.

If you installed an earlier Miracle Grove release, remove it first. Both releases use the same family names and can conflict when installed together.

Some older applications list Medium and SemiBold as separate families. That follows the four-style grouping used by legacy font menus.

## Website setup

Keep the WOFF2 files beside `miracle-grove.css`. Load the stylesheet, then use the family name in your CSS.

```css
.headline {
  font-family: "Miracle Grove", Georgia, serif;
  font-weight: 700;
  font-style: normal;
  font-synthesis: none;
  line-height: 1.2;
}

.quotation {
  font-family: "Miracle Grove", Georgia, serif;
  font-weight: 400;
  font-style: italic;
  line-height: 1.6;
}
```

The stylesheet uses `font-display: swap`. Visitors may briefly see the fallback font, so test the page while fonts are loading.

Self-host the files and load only the styles you use. Configure CORS if fonts come from a different domain.

## Numbers and alternate forms

```css
.amount { font-variant-numeric: tabular-nums; }
.prose { font-variant-numeric: proportional-nums; }
.expressive { font-feature-settings: "ss01" 1; }
```

Tabular figures align digits. Use your layout's decimal alignment separately when numbers include different currencies or punctuation.

The expressive alternates come from Fraunces. Their forms differ between the upright and italic fonts.

## Choose a suitable use

| Application | Guidance |
|---|---|
| Headings and posters | A good starting point; check spacing at the final size. |
| Short editorial passages | Try Regular with generous line height. |
| Dense body text | Proof it with readers; consider a text-focused companion. |
| Tiny labels and fine print | Not a validated strength of this release. |
| Donation totals and tables | Enable tabular figures. |
| Non-Latin text | Supply a script-appropriate fallback. |
| Email | Include system-font fallbacks; do not depend on web-font loading. |
| Embroidery and engraving | Obtain a vendor proof at production size. |

## Share documents safely

Embed fonts when your document format and application support it. Check the font list in exported PDFs before sending them to print.

The OFL permits embedding. The export process still needs to be checked in your application.

Keep text selectable on websites and in accessible documents. Allow zoom and spacing changes without fixed-height containers clipping the text.

The [quality report](quality.md) explains what was tested and what remains unverified.
