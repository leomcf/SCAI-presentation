#!/usr/bin/env python3
"""Part A: automated extraction for the 8 Mozart first movements.

For each work in corpus.csv this:
  1. Loads the .mxl score with music21.
  2. Auto-detects time signature, anacrusis, and anacrusis length.
  3. Measures whole-movement features (ambitus, estimated key, conjunct/disjunct ratio).
  4. PROPOSES authentic-cadence candidates (V(7)->I), each classified PAC vs IAC,
     for the human to adjudicate -- it does NOT decide the first PAC itself.
  5. Suggests a window boundary: the first PAC; but if no PAC arrives by measure 24
     (PAC_DEADLINE), it falls back to the strongest IAC within that span instead.

Outputs:
  features_auto.csv      -- objective, machine-extracted features (regenerable)
  cadence_candidates.csv -- proposed cadence points (PAC/IAC), ranked, for Phase 2

Run:  .venv/bin/python extract_features.py
Needs: PDMX-lib/mxl/... extracted (the score files).
"""
import csv
from music21 import converter, meter, interval, roman, key as m21key

CORPUS = "corpus.csv"
PAC_DEADLINE = 24  # if no PAC by this measure, fall back to the strongest IAC


def load_movement(score):
    """Return the first movement. PDMX files are usually a single movement already;
    if multiple, music21 still parses the whole part -- we keep it and let the
    human-chosen first PAC bound the analytical window downstream."""
    return score


def detect_meter_and_anacrusis(s):
    tss = s.recurse().getElementsByClass(meter.TimeSignature)
    ts = tss[0] if tss else None
    ts_str = ts.ratioString if ts else ""
    has_ana, ana_ql = "no", 0.0
    measures = s.parts[0].getElementsByClass("Measure") if s.parts else []
    if ts and len(measures):
        first = measures[0]
        bar_ql = ts.barDuration.quarterLength
        # an anacrusis: first measure is shorter than a full bar (paddingLeft set)
        actual = first.duration.quarterLength
        pad = getattr(first, "paddingLeft", 0) or 0
        if pad > 0 or (actual < bar_ql - 1e-6):
            has_ana = "yes"
            ana_ql = round(pad if pad > 0 else (bar_ql - actual), 4)
    return ts_str, has_ana, ana_ql


def rh_part(s):
    """Right hand = the top staff. music21 splits a piano grand staff into
    'P1-Staff1' (RH) and 'P1-Staff2' (LH). Fall back to the first part."""
    for p in s.parts:
        if str(p.id).endswith("Staff1"):
            return p
    return s.parts[0] if s.parts else s


def ambitus_of(stream):
    """semitone span, low midi, high midi over every pitch in the stream."""
    ps = [p.midi for p in stream.flatten().pitches]
    if not ps:
        return None, None, None
    return max(ps) - min(ps), min(ps), max(ps)


def line_motion(stream):
    """conjunct vs disjunct ratio on the melodic SKYLINE (highest sounding pitch
    per vertical slice). Applied to the whole texture = 'total', or to the RH part."""
    try:
        ch = stream.chordify()
    except Exception:
        ch = stream
    steps = leaps = 0
    prev = None
    for el in ch.recurse().notes:
        p = max(el.pitches, key=lambda x: x.ps) if el.isChord else el.pitch
        if prev is not None:
            semis = abs(p.ps - prev.ps)
            if semis == 0:
                pass
            elif semis <= 2:
                steps += 1
            else:
                leaps += 1
        prev = p
    total = steps + leaps
    if total == 0:
        return None, None, 0
    return round(steps / total, 3), round(leaps / total, 3), total


def cadence_candidates(s, home_key, max_candidates=20):
    """Propose V(7)->I (authentic) cadence points, each classified PAC vs IAC.
      PAC = dominant->tonic, tonic in root position, soprano on scale-degree 1.
      IAC = dominant->tonic but inverted and/or soprano on ^3 or ^5.
    These are CANDIDATES for the human to confirm -- noisy by design."""
    cands = []
    try:
        ch = s.chordify()
    except Exception:
        return cands
    chords = list(ch.recurse().getElementsByClass("Chord"))
    tonic = home_key.tonic
    for i in range(1, len(chords)):
        prev, cur = chords[i - 1], chords[i]
        try:
            rn_prev = roman.romanNumeralFromChord(prev, home_key)
            rn_cur = roman.romanNumeralFromChord(cur, home_key)
        except Exception:
            continue
        is_dom = rn_prev.romanNumeralAlone in ("V", "VII") or rn_prev.scaleDegree == 5
        is_tonic = rn_cur.romanNumeralAlone == "I" or rn_cur.scaleDegree == 1
        if not (is_dom and is_tonic):
            continue
        sop = max(cur.pitches, key=lambda x: x.ps)  # true highest = soprano
        sop_is_1 = (sop.pitchClass == tonic.pitchClass)
        root_pos = cur.inversion() == 0 and prev.inversion() == 0
        cad_type = "PAC" if (sop_is_1 and root_pos) else "IAC"
        beat = getattr(cur, "beat", None)
        cands.append({
            "cad_type": cad_type,
            "measure": cur.measureNumber,
            "beat": round(float(beat), 2) if beat is not None else "",
            "offset_ql": round(float(cur.getOffsetInHierarchy(ch)), 4),
            "soprano": sop.nameWithOctave,
            "prev_rn": str(rn_prev.figure),
            "cur_rn": str(rn_cur.figure),
            "root_position": root_pos,
        })
        if len(cands) >= max_candidates:
            break
    return cands


def suggest_boundary(cands):
    """First PAC; but if no PAC by PAC_DEADLINE, fall back to strongest IAC in span."""
    pacs = [c for c in cands if c["cad_type"] == "PAC" and c["measure"]]
    iacs = [c for c in cands if c["cad_type"] == "IAC" and c["measure"]]
    first_pac = pacs[0] if pacs else None
    if first_pac and first_pac["measure"] <= PAC_DEADLINE:
        return "PAC", first_pac
    iac_in = [c for c in iacs if c["measure"] <= PAC_DEADLINE]
    if iac_in:
        return "IAC (fallback: no PAC by m.%d)" % PAC_DEADLINE, iac_in[0]
    if first_pac:
        return "PAC (late, after m.%d)" % PAC_DEADLINE, first_pac
    if iacs:
        return "IAC (no PAC at all)", iacs[0]
    return "none found", None


def main():
    rows = list(csv.DictReader(open(CORPUS)))
    feat_out, cand_out = [], []
    for r in rows:
        wid, path = r["work_id"], r["mxl_path"]
        print(f"\n=== {wid}  ({r['year']}, {r['key_nominal']}) ===")
        try:
            s = load_movement(converter.parse(path))
        except Exception as e:
            print(f"  PARSE FAILED: {e}")
            continue
        ts_str, has_ana, ana_ql = detect_meter_and_anacrusis(s)
        try:
            est_key = s.analyze("key")
        except Exception:
            est_key = None
        home = est_key if est_key else m21key.Key(r["key_nominal"].split()[0])
        rh = rh_part(s)
        amb_t, lo_t, hi_t = ambitus_of(s)        # total: both hands
        amb_rh, lo_rh, hi_rh = ambitus_of(rh)    # right hand only
        step_t, leap_t, n_t = line_motion(s)     # total skyline
        step_rh, leap_rh, n_rh = line_motion(rh) # right-hand line
        mot_t = "disjunct" if (leap_t is not None and leap_t > 0.5) else "conjunct"
        mot_rh = "disjunct" if (leap_rh is not None and leap_rh > 0.5) else "conjunct"

        print(f"  time signature : {ts_str}   anacrusis: {has_ana} ({ana_ql} ql)")
        print(f"  estimated key  : {est_key}  (nominal {r['key_nominal']})")
        print(f"  ambitus total  : {amb_t} st   |  RH only: {amb_rh} st")
        print(f"  motion total   : {mot_t} (leap {leap_t})  |  RH: {mot_rh} (leap {leap_rh})")

        feat_out.append({
            "work_id": wid, "year": r["year"], "key_nominal": r["key_nominal"],
            "time_signature": ts_str, "has_anacrusis": has_ana, "anacrusis_ql": ana_ql,
            "estimated_key": str(est_key),
            "ambitus_total_st": amb_t, "ambitus_rh_st": amb_rh,
            "midi_low_total": lo_t, "midi_high_total": hi_t,
            "midi_low_rh": lo_rh, "midi_high_rh": hi_rh,
            "step_ratio_total": step_t, "leap_ratio_total": leap_t, "motion_total": mot_t,
            "step_ratio_rh": step_rh, "leap_ratio_rh": leap_rh, "motion_rh": mot_rh,
            "n_int_total": n_t, "n_int_rh": n_rh,
        })

        cands = cadence_candidates(s, home)
        n_pac = sum(1 for c in cands if c["cad_type"] == "PAC")
        print(f"  cadence cands  : {len(cands)} authentic ({n_pac} PAC, {len(cands)-n_pac} IAC)")
        for c in cands[:6]:
            print(f"      [{c['cad_type']}] m{c['measure']} b{c['beat']} off={c['offset_ql']}  "
                  f"{c['prev_rn']}->{c['cur_rn']}  sop={c['soprano']}  "
                  f"{'root-pos' if c['root_position'] else 'inv'}")
        label, sug = suggest_boundary(cands)
        if sug:
            print(f"  >> SUGGESTED window boundary: {label} at m{sug['measure']} "
                  f"(offset {sug['offset_ql']} ql)")
        else:
            print(f"  >> SUGGESTED window boundary: {label}")
        for c in cands:
            cand_out.append({"work_id": wid, **c})

    with open("features_auto.csv", "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(feat_out[0].keys()))
        w.writeheader(); w.writerows(feat_out)
    with open("cadence_candidates.csv", "w", newline="") as f:
        cols = ["work_id", "cad_type", "measure", "beat", "offset_ql", "soprano",
                "prev_rn", "cur_rn", "root_position"]
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader(); w.writerows(cand_out)
    print("\n-> wrote features_auto.csv and cadence_candidates.csv")


if __name__ == "__main__":
    main()
