#!/usr/bin/env python3
"""Turn features_auto.csv into presentation-ready charts (French labels).

Outputs PNGs at 150 dpi, ready to drop into Google Slides:
  fig_timeline.png          -- ambitus / leap / step vs composition year
  fig_circle_of_fifths.png  -- home keys placed on the circle of fifths

NOTE: these currently plot WHOLE-MOVEMENT features. Once pac_annotations.csv is
filled, re-run extract_features on the opening->first-PAC windows and this same
script regenerates the figures on the windowed data.
"""
import csv
import numpy as np
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150,
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
    "axes.spines.right": False,
})
MAJ, MIN = "#2c6fbb", "#c0392b"   # major = blue, minor = red (highlight)

rows = list(csv.DictReader(open("features_auto.csv")))
def col(name, cast=float):
    return [cast(r[name]) for r in rows]

years   = col("year", int)
labels  = [r["work_id"].replace("/i", "") for r in rows]
is_min  = ["minor" in r["key_nominal"] for r in rows]
colors  = [MIN if m else MAJ for m in is_min]


def jitter_years(ys):
    """nudge coincident years apart so labels don't overlap (1789 has two)."""
    ys = list(ys); seen = {}
    out = []
    for y in ys:
        k = seen.get(y, 0); seen[y] = k + 1
        out.append(y + k * 0.18)
    return out


def timeline():
    # (total column, RH column, y-label, title). Filled marker = RH (melody),
    # hollow marker = total (both hands).
    feats = [
        ("ambitus_total_st", "ambitus_rh_st", "Ambitus (demi-tons)", "Étendue de l'ambitus"),
        ("leap_ratio_total", "leap_ratio_rh", "Proportion de sauts", "Mouvement disjoint (sauts)"),
        ("step_ratio_total", "step_ratio_rh", "Proportion conjointe", "Mouvement conjoint (degrés)"),
    ]
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.8))
    xs = jitter_years(years)
    for ax, (kt, krh, ylab, title) in zip(axes, feats):
        yt, yrh = col(kt), col(krh)
        # connect RH points in chronological order
        order = sorted(range(len(years)), key=lambda i: years[i])
        ax.plot([xs[i] for i in order], [yrh[i] for i in order],
                color="#999", lw=1, zorder=1, alpha=0.5)
        # total = hollow, RH = filled, thin grey link between the pair
        for x, vt, vrh, c in zip(xs, yt, yrh, colors):
            ax.plot([x, x], [vt, vrh], color="#bbb", lw=0.8, zorder=1)
        ax.scatter(xs, yt, facecolors="none", edgecolors=colors, s=120,
                   linewidth=1.6, zorder=2)
        ax.scatter(xs, yrh, c=colors, s=120, zorder=3, edgecolor="white", linewidth=1.2)
        for x, y, lab in zip(xs, yrh, labels):
            ax.annotate(lab, (x, y), xytext=(0, -13), textcoords="offset points",
                        ha="center", fontsize=8)
        ax.set_title(title); ax.set_xlabel("Année de composition"); ax.set_ylabel(ylab)
        ax.set_xticks([1775, 1778, 1781, 1784, 1787, 1790])
    handles = [plt.Line2D([], [], marker="o", ls="", color=MAJ, label="Majeur"),
               plt.Line2D([], [], marker="o", ls="", color=MIN, label="Mineur"),
               plt.Line2D([], [], marker="o", ls="", mfc="none", mec="#444", label="Total (2 mains)"),
               plt.Line2D([], [], marker="o", ls="", color="#444", label="Main droite (mélodie)")]
    fig.legend(handles=handles, loc="upper right", frameon=False, fontsize=9)
    fig.suptitle("Mozart, premiers mouvements : traits au fil du temps (jeune → vieux)",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.92])
    fig.savefig("fig_timeline.png"); print("-> fig_timeline.png")


def parse_key(nominal):
    """Build a music21 Key from a 'B-flat major' / 'A minor' style string."""
    from music21 import key as m21key
    parts = nominal.split()
    tonic = parts[0].replace("-flat", "-").replace("-sharp", "#")
    mode = parts[1] if len(parts) > 1 else "major"
    return m21key.Key(tonic, mode)


def circle_of_fifths():
    # spokes labelled in conventional circle-of-fifths order (flats on the flat side)
    tick_labels = ["C", "G", "D", "A", "E", "B", "F#/Gb", "Db", "Ab", "Eb", "Bb", "F"]
    fig = plt.figure(figsize=(7, 7))
    ax = fig.add_subplot(111, projection="polar")
    ax.set_theta_zero_location("N"); ax.set_theta_direction(-1)
    ax.set_xticks(np.deg2rad(np.arange(0, 360, 30)))
    ax.set_xticklabels(tick_labels); ax.set_yticks([]); ax.set_ylim(0, 1.2)

    from collections import Counter
    cnt = Counter(); pts = []
    for r in rows:
        k = parse_key(r["key_nominal"])
        sharps = k.sharps               # -7..+7 = position on the circle of fifths
        minor = (k.mode == "minor")
        cnt[(sharps, minor)] += 1
        pts.append((sharps, minor, r["work_id"].replace("/i", "")))
    drawn = {}
    for sharps, minor, lab in pts:
        ang = np.deg2rad((sharps % 12) * 30)   # music21's .sharps drives the angle
        radius = 0.6 if minor else 1.0          # minor inner ring (at its relative major)
        key_ = (sharps, minor); n = cnt[key_]
        ax.scatter([ang], [radius], s=120 + 120 * (n - 1),
                   c=(MIN if minor else MAJ), edgecolor="white", linewidth=1.5, zorder=3)
        marker_radius_pt = np.sqrt((120 + 120 * (n - 1)) / np.pi)
        base = marker_radius_pt + 7
        seen = drawn.get(key_, 0); drawn[key_] = seen + 1
        ax.annotate(lab, (ang, radius), xytext=(0, -(base + 11 * seen)),
                    textcoords="offset points", ha="center", fontsize=8)
    ax.set_title("Tonalités sur le cycle des quintes — position via music21 (.sharps)\n"
                 "majeur = anneau extérieur · mineur = intérieur (au degré de son relatif majeur)",
                 pad=20, fontsize=11)
    fig.tight_layout()
    fig.savefig("fig_circle_of_fifths.png"); print("-> fig_circle_of_fifths.png")


if __name__ == "__main__":
    timeline()
    circle_of_fifths()
