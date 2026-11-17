# Sherwin Carlquist Digital Extended Specimen Network

Public site for the Sherwin Carlquist Digital Extended Specimen Network, a collaboration between the Botanical Research Institute of Texas (BRIT) at the Fort Worth Botanic Garden and the California Botanic Garden, supported by NSF Awards 2133562 (BRIT) and 2133561 (CalBG).

The site links Sherwin Carlquist's botanical specimens, field images, publications, and archival materials into a unified, interoperable resource, following the Extended Specimen Network framework.

Published at: **https://britorg.github.io/carlquist_esn/**

## Pages

- `index.html` — landing page: project overview, quick links, and sections for Collections, Data & Tools, Products, and Partners.
- `extended_specimen.html` — an interactive diagram mapping project resources onto the Extended Specimen Network framework. Hover a bubble for a description; click an active bubble to open the underlying resource.
- `publications_explorer.html` — an interactive dashboard for browsing, filtering, and visualizing all 346 known Carlquist publications (1956–2021), sourced from the companion [publications dataset](https://github.com/BRITorg/carlquist_publications_dataset) ([Zenodo](https://doi.org/10.5281/zenodo.18687469), CC0).

## LLM-readable files

- `llms.txt` — concise, [llmstxt.org](https://llmstxt.org/)-style index of the site's pages, data, and collections, for LLMs and agents.
- `llms-full.txt` — expanded plain-text version of the site content, including the full list of 346 publications (which the explorer only renders with JavaScript). The publications dataset covers publications only, which is one component of the network.

## Updating publication data

The publications data is generated, not hand-edited. With the [publications dataset](https://github.com/BRITorg/carlquist_publications_dataset) checked out as a sibling directory (`../carlquist_publications_dataset`):

```
python3 tools/build_site_data.py          # regenerate and write changes
python3 tools/build_site_data.py --check  # report only; exit 1 if the site is stale
python3 tools/build_site_data.py --dataset /path/to/dataset
```

This rewrites the embedded `RAW` JSON in `publications_explorer.html`, the publications list in `llms-full.txt`, and the publication counts quoted in the pages, README, and `llms.txt`. It uses only the Python standard library. Review `git diff`, then commit and push; GitHub Pages publishes the result.
