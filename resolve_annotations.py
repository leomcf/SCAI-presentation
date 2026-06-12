#!/usr/bin/env python3
"""Resolve the hand annotations into one analysis-ready table.

You edit ONLY pac_annotations.csv (5 human columns). This script fills the rest:

Reads:
  pac_annotations.csv  -- HUMAN judgments: first_pac_measure, first_pac_beat,
                          pac_key, n_evaded_before, justification
  features_auto.csv    -- objective features (time_signature, anacrusis) from music21
  corpus.csv           -- work metadata + .mxl paths (year, title, key)

Computes:
  first_pac_offset_ql  -- quarter-notes from the start of the movement to the PAC,
                          derived from (measure, beat) via music21. This is the
                          meter- and anacrusis-proof position used for comparison.

Writes:
  pac_resolved.csv     -- GENERATED, do not hand-edit. Re-run after editing annotations.

Beat convention: 'beat' is counted as music21 counts it (e.g. 6/8 has 2 dotted-quarter
beats), matching the 'beat' values in cadence_candidates.csv -- so you can cross-reference.

Run:  .venv/bin/python resolve_annotations.py
"""
import csv
from music21 import converter, meter


def load(path, key="work_id"):
    return {r[key]: r for r in csv.DictReader(open(path))}


def offset_of(mxl_path, measure_num, beat):
    """Quarter-note offset from movement start to (measure, beat). '' if not yet filled."""
    if not mxl_path or not measure_num or beat in (None, ""):
        return ""
    try:
        part = converter.parse(mxl_path).parts[0]
    except Exception:
        return ""
    target = int(float(measure_num))
    for m in part.getElementsByClass("Measure"):
        if m.measureNumber == target:
            ts = m.timeSignature or m.getContextByClass(meter.TimeSignature)
            beat_ql = ts.beatDuration.quarterLength if ts else 1.0
            return round(m.offset + (float(beat) - 1) * beat_ql, 4)
    return ""  # measure number not found in the score


def main():
    ann = load("pac_annotations.csv")
    feats = load("features_auto.csv")
    corpus = load("corpus.csv")

    cols = ["work_id", "year", "title", "key_nominal", "time_signature",
            "has_anacrusis", "anacrusis_ql", "first_pac_measure", "first_pac_beat",
            "first_pac_offset_ql", "pac_key", "n_evaded_before", "justification"]
    out = []
    for wid, a in ann.items():
        f, c = feats.get(wid, {}), corpus.get(wid, {})
        offset = offset_of(c.get("mxl_path", ""),
                           a.get("first_pac_measure"), a.get("first_pac_beat"))
        out.append({
            "work_id": wid, "year": c.get("year", ""), "title": c.get("title", ""),
            "key_nominal": c.get("key_nominal", ""),
            "time_signature": f.get("time_signature", ""),
            "has_anacrusis": f.get("has_anacrusis", ""), "anacrusis_ql": f.get("anacrusis_ql", ""),
            "first_pac_measure": a.get("first_pac_measure", ""),
            "first_pac_beat": a.get("first_pac_beat", ""),
            "first_pac_offset_ql": offset, "pac_key": a.get("pac_key", ""),
            "n_evaded_before": a.get("n_evaded_before", ""),
            "justification": a.get("justification", ""),
        })
    out.sort(key=lambda r: int(r["year"]) if r["year"] else 0)

    with open("pac_resolved.csv", "w", newline="") as fp:
        w = csv.DictWriter(fp, fieldnames=cols)
        w.writeheader(); w.writerows(out)
    filled = sum(1 for r in out if r["first_pac_offset_ql"] != "")
    print(f"-> pac_resolved.csv  ({filled}/{len(out)} works have a resolved PAC offset)")


if __name__ == "__main__":
    main()
