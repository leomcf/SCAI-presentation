#!/usr/bin/env python3
"""Render the first N measures of a corpus work to a PNG, via music21 + MuseScore 3.

Used to put a notated excerpt on the cadence example slides (e.g. K.570 IAC).
Reads the mxl path from corpus.csv so it stays in sync with the rest of the pipeline.
"""
import csv
import sys
from pathlib import Path

from music21 import converter, environment

# Point music21 at the locally installed MuseScore 3 for PNG export.
MSCORE = "/Applications/MuseScore 3.app/Contents/MacOS/mscore"
us = environment.UserSettings()
us["musicxmlPath"] = MSCORE
us["musescoreDirectPNGPath"] = MSCORE


def row_for(work_id):
    for r in csv.DictReader(open("corpus.csv")):
        if r["work_id"] == work_id:
            return r
    raise SystemExit(f"work_id {work_id} not found in corpus.csv")


def render(work_id, n_measures, out):
    row = row_for(work_id)
    score = converter.parse(row["mxl_path"])
    excerpt = score.measures(1, n_measures)
    # Replace the raw PDMX hash filename with a clean, human title.
    from music21 import metadata as m21meta
    md = m21meta.Metadata()
    work = work_id.replace("/i", "")
    md.title = f"Mozart — Sonate {work}, mes. 1–{n_measures}"
    md.composer = "W. A. Mozart (1756–1791)"
    excerpt.metadata = md
    written = excerpt.write("musicxml.png", fp=out)
    # MuseScore may emit "<out>-1.png"; normalise to the requested name.
    written = Path(written)
    final = Path(out)
    if written != final and written.exists():
        written.replace(final)
    print(f"-> {final}")


if __name__ == "__main__":
    work = sys.argv[1] if len(sys.argv) > 1 else "K.570/i"
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 12
    out = sys.argv[3] if len(sys.argv) > 3 else "fig_iac_k570_score.png"
    render(work, n, out)
