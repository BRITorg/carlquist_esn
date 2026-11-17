#!/usr/bin/env python3
"""Regenerate publication-derived content in this site from the dataset repo.

Source of truth: BRITorg/carlquist_publications_dataset (local sibling checkout
by default). Reads its three CSVs and updates, in place:

  1. publications_explorer.html  - the inline `const RAW = {...};` literal
  2. llms-full.txt               - the "## Publications (N, chronological)" list
  3. publication counts quoted in prose (index.html, README.md, llms.txt,
     llms-full.txt, extended_specimen.html, publications_explorer.html)

Usage:
  python3 tools/build_site_data.py                  # write changes
  python3 tools/build_site_data.py --check          # report only; exit 1 if stale
  python3 tools/build_site_data.py --dataset PATH   # other dataset checkout

Standard library only. Run from anywhere.
"""
import argparse
import csv
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DEFAULT_DATASET = ROOT.parent / "carlquist_publications_dataset"

EXPLORER = ROOT / "publications_explorer.html"
LLMS_FULL = ROOT / "llms-full.txt"
COUNT_FILES = [
    "index.html", "README.md", "llms.txt", "llms-full.txt",
    "extended_specimen.html", "publications_explorer.html",
]

RAW_START = "const RAW = "
RAW_END = ";\nconst PUBS = RAW.pubs;"


def read_csv(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def build_raw(ds):
    pubs = []
    for r in read_csv(ds / "carlquist_publications.csv"):
        pubs.append({
            "title": r["title"],
            "journal": r["container-title"],
            "year": int(r["year"]),
            "issued": r["issued"],
            "authors": [a.strip() for a in r["author"].split(";") if a.strip()],
            "volume": r["volume"],
            "issue": r["issue"],
            "page": r["page"],
            "type": r["type"],
            "doi": r["DOI"],
            "wikidata": r["wikidata-url"],
            "url": r["URL"],
        })
    authors = {
        r["author-as-cited"]: {
            "full": r["author-full"],
            "reconciled": r["author-full-reconciled"],
            "wikidata": r["wikidata-url"],
        }
        for r in read_csv(ds / "carlquist_authors.csv")
    }
    journals = {
        r["journal-title"]: {"wikidata": r["wikidata-url"], "issn": r["ISSN"]}
        for r in read_csv(ds / "carlquist_journals.csv")
    }
    return {"pubs": pubs, "authors": authors, "journals": journals}


def llms_line(p):
    cite = p["journal"]
    if cite:
        if p["volume"]:
            cite += " " + p["volume"] + (f"({p['issue']})" if p["issue"] else "")
        if p["page"]:
            cite += ": " + p["page"]
    auth = "; ".join(p["authors"])
    parts = [f"{p['year']}.", auth if auth.endswith(".") else auth + ".", p["title"] if p["title"].endswith(".") else p["title"] + "."]
    if cite:
        parts.append(cite if cite.endswith(".") else cite + ".")
    if p["doi"]:
        parts.append("https://doi.org/" + p["doi"])
    elif p["url"]:
        parts.append(p["url"])
    if p["wikidata"]:
        parts.append(p["wikidata"])
    return "- " + " ".join(parts)


def sort_for_llms(pubs):
    return sorted(pubs, key=lambda p: (p["year"], p["issued"]))


def replace_raw(html, raw):
    i = html.index(RAW_START)
    j = html.index(RAW_END, i)
    old = json.loads(html[i + len(RAW_START):j])
    new = RAW_START + json.dumps(raw, ensure_ascii=True)
    return html[:i] + new + html[j:], old


def replace_llms_list(txt, pubs):
    head = re.search(r"^## Publications \(\d+, chronological\)\n", txt, re.M)
    if not head:
        sys.exit("llms-full.txt: publications heading not found")
    first = re.search(r"^- \d{4}\. ", txt[head.end():], re.M)
    if not first:
        sys.exit("llms-full.txt: publications list not found")
    start = head.end() + first.start()
    lines = "\n".join(llms_line(p) for p in sort_for_llms(pubs)) + "\n"
    txt = txt[:head.start()] + f"## Publications ({len(pubs)}, chronological)\n" + txt[head.end():start] + lines
    return txt


def update_counts(txt, new_n):
    # Any "NNN [known] [Carlquist] publications" is set to the current count.
    pat = re.compile(r"(?<!than )\b\d{3}\b(?= (?:known )?(?:Carlquist )?publications)")
    return pat.sub(str(new_n), txt)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--dataset", type=Path, default=DEFAULT_DATASET)
    ap.add_argument("--check", action="store_true", help="don't write; exit 1 if out of date")
    args = ap.parse_args()

    ds = args.dataset.resolve()
    if not (ds / "carlquist_publications.csv").exists():
        sys.exit(f"dataset not found at {ds} (use --dataset)")
    try:
        ver = subprocess.run(["git", "-C", str(ds), "describe", "--tags", "--always", "--dirty"],
                             capture_output=True, text=True).stdout.strip()
    except OSError:
        ver = "?"

    raw = build_raw(ds)
    new_n = len(raw["pubs"])

    html, old_raw = replace_raw(EXPLORER.read_text(encoding="utf-8"), raw)
    old_n = len(old_raw["pubs"])
    changes = {EXPLORER: html}

    llms = replace_llms_list(LLMS_FULL.read_text(encoding="utf-8"), raw["pubs"])
    changes[LLMS_FULL] = llms

    for name in COUNT_FILES:
        p = ROOT / name
        base = changes.get(p, p.read_text(encoding="utf-8"))
        changes[p] = update_counts(base, new_n)

    stale = []
    for p, text in changes.items():
        if p.read_text(encoding="utf-8") != text:
            stale.append(p)
            if not args.check:
                p.write_text(text, encoding="utf-8")

    print(f"dataset: {ds} ({ver})")
    print(f"publications: {old_n} -> {new_n}; "
          f"authors: {len(old_raw['authors'])} -> {len(raw['authors'])}; "
          f"journals: {len(old_raw['journals'])} -> {len(raw['journals'])}")
    verb = "out of date" if args.check else "updated"
    for p in stale:
        print(f"  {verb}: {p.relative_to(ROOT)}")
    if not stale:
        print("  site is up to date")
    if args.check and stale:
        sys.exit(1)


if __name__ == "__main__":
    main()
