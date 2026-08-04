#!/usr/bin/env python3
"""Fail if the README's rate tables disagree with the JSON data files.

The README is the page a human reads and the part most likely to be quoted or
screenshotted. It is also the part most likely to go stale, because updating
the generator regenerates the JSON but not the prose. This check makes that
divergence a build failure rather than a credibility problem discovered by a
reader.

Parses the two markdown tables in the README that restate generated figures
(the zero-emission row and the PHEV range table) and compares them against
appropriate-percentages.json and phev-range-bands.json.
"""

import json
import re
import sys

YEARS = ["2026/27", "2027/28", "2028/29", "2029/30"]

failures = []


def fail(msg: str) -> None:
    failures.append(msg)
    print(f"::error::{msg}")


readme = open("README.md", encoding="utf-8").read()


def cells(row: str) -> list[str]:
    return [c.strip() for c in row.strip().strip("|").split("|")]


def pct(text: str) -> int | None:
    m = re.fullmatch(r"(\d+)%", text.strip())
    return int(m.group(1)) if m else None


# ── Zero-emission row ──────────────────────────────────────────────────────
ap = json.load(open("appropriate-percentages.json", encoding="utf-8"))
expected_ev = {r["taxYear"]: r["appropriatePercentage"] for r in ap["zeroEmission"]["byTaxYear"]}

ev_match = re.search(
    r"\*\*Zero-emission.*?\n\n\|(.+?)\|\n\|[-\s|]+\|\n\|(.+?)\|\n",
    readme,
    re.S,
)
if not ev_match:
    fail("README: could not find the zero-emission table")
else:
    hdr = cells(ev_match.group(1))
    vals = cells(ev_match.group(2))
    if hdr != YEARS:
        fail(f"README zero-emission header {hdr} != {YEARS}")
    else:
        for year, cell in zip(hdr, vals):
            got, want = pct(cell), expected_ev.get(year)
            if got != want:
                fail(f"README zero-emission {year}: says {got}%, data says {want}%")

# ── PHEV range table ───────────────────────────────────────────────────────
phev = json.load(open("phev-range-bands.json", encoding="utf-8"))
expected_phev = {b["label"]: b["byTaxYear"] for b in phev["bands"]}

# `(?:\|.*\|\n)+` alone runs past the table's blank-line terminator and swallows
# following prose and the next table, so require each captured line to be a real
# table row: pipe, non-newline content, pipe, to end of line.
phev_match = re.search(
    r"\| Electric range \|[^\n]*\n\|[-\s|]+\|\n((?:\|[^\n]*\|\n)+)",
    readme,
)
if not phev_match:
    fail("README: could not find the PHEV range table")
else:
    seen = set()
    for row in phev_match.group(1).strip().split("\n"):
        c = cells(row)
        label, values = c[0], c[1:]
        if label not in expected_phev:
            fail(f"README PHEV row '{label}' has no matching band in phev-range-bands.json")
            continue
        seen.add(label)
        for year, cell in zip(YEARS, values):
            got, want = pct(cell), expected_phev[label].get(year)
            if got != want:
                fail(f"README PHEV '{label}' {year}: says {got}%, data says {want}%")
    missing = set(expected_phev) - seen
    if missing:
        fail(f"README PHEV table is missing bands present in the data: {sorted(missing)}")

# ── eVED rates ─────────────────────────────────────────────────────────────
eved = json.load(open("eved.json", encoding="utf-8"))
rates = eved["ratesPerMile"]
# README states these in pence; JSON stores pounds.
for label, key, pence in [
    ("Battery electric", "electric", rates["electric"] * 100),
    ("Plug-in hybrid", "plugInHybrid", rates["plugInHybrid"] * 100),
]:
    row = re.search(rf"\| {re.escape(label)} \| ([^|]+) \|", readme)
    if not row:
        fail(f"README: no eVED row for {label}")
        continue
    m = re.fullmatch(r"([\d.]+)p", row.group(1).strip())
    if not m:
        fail(f"README eVED {label}: unparseable value '{row.group(1).strip()}'")
    elif abs(float(m.group(1)) - pence) > 1e-9:
        fail(f"README eVED {label}: says {m.group(1)}p, data says {pence:g}p")

if failures:
    print(f"\n{len(failures)} mismatch(es) between README and data files.")
    sys.exit(1)

print("README rate tables match the JSON data files.")
