# Build the fonts

Use Python 3.13 for the tested build. The source fonts are included, so the build does not fetch upstream files at runtime.

## Set up an environment

```sh
python -m venv .venv
```

Activate it with `.venv\Scripts\Activate.ps1` in PowerShell or `source .venv/bin/activate` on macOS and Linux.

```sh
python -m pip install -r requirements.txt
python scripts/build.py
python scripts/test_fonts.py
```

The build writes eight TTF files and eight WOFF2 files to `fonts`. It also writes the stylesheet and checksums.

## Understand the inputs

`upstream/lock.json` records the distribution revision and hashes. The build stops if any vendored input differs from its recorded hash.

The custom outlines and transformations are defined in `scripts/build.py`. The project currently uses Python and TrueType inputs rather than editable UFO sources.

The upstream project's design sources remain available in [the Fraunces repository](https://github.com/undercasetype/Fraunces).

## Check reproducibility

```sh
python scripts/build.py --output build/repro-check
python scripts/test_fonts.py --compare build/repro-check
```

Font timestamps are fixed. With the pinned build dependencies, repeated local builds produce identical font bytes.

CI checks repeated builds on its own runner. Cross-platform byte identity requires a comparison of the outputs from both operating systems.

## Run the independent audit

```sh
python -m pip install -r requirements-audit.txt
python scripts/audit.py
```

FontBakery reports go into `build/audit`. Warnings remain visible; errors, fatal results, or failures make the audit command fail.

The audit dependency file pins FontBakery itself, but not every transitive dependency. Save the environment details with any published audit.

## Prepare a release

```sh
python scripts/package_release.py
```

This creates a ZIP in `dist` with desktop fonts, web files, license, and usage notes. It also writes a SHA-256 checksum.

Update version metadata and the changelog before publishing changed fonts. Review visual proofs alongside automated tests; a passing script does not judge every letter pair.
