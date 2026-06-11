# Pipeline — Mozart sonata first movements, opening → first PAC

**Project (revised scope):** Drop Brahms. Analyze the **first movements of 8 Mozart piano sonatas**, spanning his life (1775–1789). For each, study the music **from the opening up to the first perfect authentic cadence (PAC) in the home key**. Compare features chronologically — *young Mozart vs. old Mozart*.

Why this scope: PDMX has 169 clean Mozart piano-solo candidates (vs. 36 noisy Brahms), the first-movement-to-first-PAC window is a theoretically grounded unit (not an arbitrary bar count), and intra-composer evolution is a more original question than a Classical-vs-Romantic contrast.

## Model recommendation
Use `claude-opus-4-8` — strongest reasoning for music theory, code generation, and result interpretation, so code works first try under time pressure.

---

## The corpus (locked)

| # | Work | Year | Key | PDMX title | Note |
|---|------|------|-----|------------|------|
| 1 | K.279/i (No.1) | 1775 | C | Piano Sonata No 1 Mozart KV 279 | full sonata — slice mvt I |
| 2 | K.309/i (No.7) | 1777 | C | sonate mozart n7 C M | verify mvt I |
| 3 | K.310/i (No.8) | 1778 | A min | Mozart Sonata No.8 KV.310 1st | first minor-key |
| 4 | K.330/i (No.10) | 1783 | C | Sonate in C KV 330-1.Allegro moderato | clean single mvt |
| 5 | K.457/i (No.14) | 1784 | C min | Mozart: Klaviersonate KV 457 - 1 expozice | exposition only |
| 6 | K.545/i (No.16) | 1788 | C | Sonata No. 16 K. 545 (1st movement) | "facile" |
| 7 | K.570/i (No.17) | 1789 | B♭ | Mozart - Sonata in Bb K 570 Movement I | late anchor |
| 8 | K.576/i (No.18) | 1789 | D | Mozart - Piano Sonata No. 18 in D: Allegro | his last sonata |

Excluded **K.331/i** (theme & variations, not sonata-allegro). Composition years are the chronological x-axis.

---

## Phase 1 — Confirm & fetch scores (30 min)
Stage 2 of the funnel: for each of the 8, open its metadata JSON (`data.score.instrumentations[].uri == "piano-solo"`) to confirm true solo instrumentation, then resolve the `mxl` path. Needs **`mxl.tar.gz`** from Zenodo extracted into `PDMX-lib/` — that holds the actual MusicXML music21 reads.

For K.279 (full sonata) slice movement I; for K.457 (exposition) use as-is. Record final file paths in a small `corpus.csv` (work, year, key, mxl_path).

## Phase 2 — Define the analytical window: first PAC (human-in-the-loop)
This is the methodological core (see the PAC note at the bottom). For each movement:
1. **music21 proposes** cadence candidates: `chordify()` → Roman-numeral analysis → flag V(7)→I points.
2. **You adjudicate** the first PAC in the home key (V→I, soprano on scale-degree 1, both root position) and record it as data:

```
# pac_annotations.csv
work,key,first_pac_measure,first_pac_beat,justification,n_evaded_before
K.279/i,C,...,...,"root-pos V7-I, sop ^1",...
```

This annotation file is itself a deliverable. The window for each work = opening through `first_pac_measure`.

## Phase 3 — Feature extraction with music21 (1–1.5 hrs)
Run over each opening→first-PAC window:

| Feature | music21 call / method |
|---|---|
| Key / tonality | `window.analyze('key')` |
| Ambitus | `analysis.discrete.Ambitus().getPitchSpan(window)` |
| Phrase length | segment by rests/cadences, count bars |
| Motion type (conjunct/disjunct) | leaps / total melodic intervals; > 0.5 → disjunct |
| Cadence types before the PAC | from the Phase-2 candidate list (HC, IAC, evaded) |
| **Bars-to-first-PAC** | `first_pac_measure` − 1 (a feature in itself) |
| Stufen (Schenkerian) | scale-degree chords (I, II, V) in harmonic reduction |

**Bars-to-first-PAC** is the standout metric: does Mozart delay tonal closure more in late works? How many cadences does he evade first?

## Phase 3.5 — MEI (skip it)
MusicXML throughout. MEI tagging (manual or Verovio) isn't worth the time for a few-hours project.

## Phase 4 — Visualizations (45 min)
- **Chronological timeline (the heart of it):** each feature on Y, composition **year** on X. One small-multiple panel per feature. Plus a **young-half vs old-half** bar chart (4 earliest vs 4 latest works) for the cleanest single slide.
- **Bars-to-first-PAC over time:** the signature plot.
- **Circle of fifths:** map home keys / first-PAC keys on a polar matplotlib chart.
- **Schenkerian reductions:** hand-do 2–3 representative early-vs-late pairs; render excerpts via MuseScore PNG or music21 `show()`. For simultaneous playback, export two MIDIs and merge in Audacity/GarageBand.

## Phase 5 — Audio for slides (20 min)
`window.write('midi', fp=...)` → convert MIDI→MP3 (timidity or GarageBand). Embed **MP3** in Slides (MIDI won't play in-browser).

## Phase 6 — Google Slides (30 min)
1. Title + revised scope (Mozart-only, opening→first-PAC, young vs old)
2. Method slide: the human-in-the-loop PAC pipeline (computer proposes, human adjudicates, annotations as data)
3. Bars-to-first-PAC over Mozart's life — signature finding
4. Feature timelines (ambitus, motion, cadence variety) young vs old
5. Circle-of-fifths key map
6. 1–2 early/late audio + score comparisons (with Schenkerian reduction)
7. Limitations: n=8, amateur transcriptions — trends illustrative, not statistical

Share via Drive link for the professor.

---

## Environment
- Local `.venv` at `/Users/leomcfadden/SCAI/.venv` (pandas, music21, matplotlib installed). Run with `.venv/bin/python`.
- Colab alternative: `!pip install music21 matplotlib` (pandas preinstalled). Recommend local — data is already here.

## On the PAC method (DH framing — see chat)
Hand-identifying PACs is the **right** approach for a DH project *if framed as deliberate human-in-the-loop*, not "we couldn't automate it": computer does scalable objective measurement, human does the interpretive boundary that tools do unreliably, and the manual judgments are recorded as a documented, shareable dataset with justifications. Optional bonus study: measure how often music21's automated cadence detection agrees with your manual labels.

## Open questions answered
- **MEI vs MusicXML:** MusicXML throughout.
- **Colab vs local:** Local — data and venv are here.
- **Scope change:** Mozart-only narrows the deliverable but deepens it; confirm the professor's prompt allows dropping the openings-vs-finales / two-composer framing.
