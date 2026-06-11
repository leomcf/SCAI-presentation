#!/usr/bin/env python3
"""Stage 1: funnel the PDMX index down to Mozart/Brahms piano-solo candidates.

SETUP (one time):
    python3 -m venv .venv
    .venv/bin/pip install pandas
    # (music21 + matplotlib needed later for analysis, not for this script)

RUN:
    .venv/bin/python filter_corpus.py

EXPECTS:
    PDMX-lib/PDMX.csv   (the 225 MB index from Zenodo record 15571083)

OUTPUTS:
    candidates_mozart.csv, candidates_brahms.csv  (full filtered lists)
    + prints the 15 most-viewed of each to the terminal

HOW THE PIANO-SOLO FILTER WORKS:
    The `tracks` column is MIDI program numbers joined by '-'.
      '0'   -> one Acoustic Grand Piano track  => piano SOLO  (kept)
      '0-0' -> two piano tracks                => piano duo   (excluded)
    Composer is matched on the free-text `composer_name` column.
"""
import pandas as pd

CSV = "PDMX-lib/PDMX.csv"

df = pd.read_csv(CSV, low_memory=False)
print(f"total rows in PDMX: {len(df):,}")

name = df["composer_name"].fillna("").str.lower()
is_mozart = name.str.contains("mozart")
is_brahms = name.str.contains("brahms")
is_piano_solo = (df["n_tracks"] == 1) & (df["tracks"].astype(str) == "0")

cols = ["composer_name", "title", "song_length.bars", "n_notes",
        "rating", "n_views", "is_best_arrangement", "metadata", "mxl"]

for label, mask in (("Mozart", is_mozart), ("Brahms", is_brahms)):
    sub = df[mask & is_piano_solo][cols].copy()
    sub = sub.sort_values("n_views", ascending=False)
    print(f"\n=== {label}: {len(sub)} piano-solo candidates ===")
    for _, r in sub.head(15).iterrows():
        print(f"  views={int(r['n_views']):>7}  bars={r['song_length.bars']:>5}  "
              f"rating={r['rating']:>4}  {str(r['title'])[:55]}")
    # save full candidate list for stage 2
    sub.to_csv(f"candidates_{label.lower()}.csv", index=False)
    print(f"  -> wrote candidates_{label.lower()}.csv")
