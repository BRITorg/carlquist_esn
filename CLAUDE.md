# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

The public site for the Sherwin Carlquist Digital Extended Specimen Network, a BRIT/FWBG + California Botanic Garden project (NSF Awards 2133562 & 2133561) linking Carlquist's botanical specimens, field images, publications, and archival materials. Repo: `BRITorg/carlquist_esn`, deployed as a static site (no build step, no server).

## Structure

Three self-contained static HTML files — each has its own inline `<style>` and `<script>`, no shared JS/CSS files, no bundler, no package.json:

- `index.html` — landing page: project intro, quick links, Collections/Data & Tools/Products/Partners sections.
- `extended_specimen.html` — an inline hand-coded SVG diagram (concentric rings = Primary/Secondary/Tertiary Extension) with hover tooltips and clickable bubbles that link out to the actual resource (publications explorer, CCH2 portal, Portal to Texas History, etc.). Bubble state (`has` = represented in the network vs `dim` = part of the broader ESN framework but not yet represented) is set per-`<g class="esn-bubble">` via `data-status`/`data-href`/`data-desc` attributes, matched by a single tooltip-positioning script at the bottom of the file.
- `publications_explorer.html` — a client-side dashboard (uses Chart.js from a CDN) over Carlquist's full 343-item bibliography. All publication data is embedded as one inline JSON literal (`const RAW = {"pubs": [...], "authors": [...], "journals": [...]}`) near the top of the main `<script>` block — there is no external data fetch. Filtering/sorting/pagination is plain vanilla JS driven by a single `state` object and a `rerender()` function; view state (filters, sort, page) persists to `localStorage` under the key `carlquist-dash-v1`.

## Working in this repo

- There is no build, lint, or test tooling — edit the HTML files directly and open them in a browser (or a local static server) to verify changes.
- Because `publications_explorer.html` has its full dataset on a single very long line, prefer `grep`/`awk`/targeted `Read` offsets over reading the whole file at once when working in it — a naive full read will blow past normal tool output limits.
- The canonical source of the publications dataset is the companion dataset repo (`BRITorg/carlquist_publications_dataset`, published on Zenodo, CC0, CSL-JSON/Dublin Core). If the dataset changes, the embedded `RAW` JSON in `publications_explorer.html` needs to be regenerated/re-pasted from that source — don't hand-edit individual publication records unless correcting a one-off display bug.
- All three pages share the same CSS custom-property palette (`--bg`, `--ink`, `--accent`, etc. defined in each page's own `:root`) and the same header/nav-strip/footer visual pattern — keep new pages visually consistent with this rather than introducing a new style.
- The footer contact link on each page assembles a `mailto:` at runtime from `data-u`/`data-d` attributes specifically to dodge static-page email scrapers and Cloudflare's email-obfuscation rewrite; don't "simplify" this back to a plain `mailto:` href.
- Google Analytics (GA4, measurement ID `G-QDL0NZLDKZ`) is loaded on every page via the same inline snippet — keep it in sync if adding new pages.
