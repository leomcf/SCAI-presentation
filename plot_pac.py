#!/usr/bin/env python3
"""Plot the first-PAC findings from pac_resolved.csv (French labels).

Run this AFTER filling pac_annotations.csv and running resolve_annotations.py.

Output:
  fig_pac_timeline.png
    left  : temps jusqu'a la 1re CP (offset_ql) vs annee de composition,
            taille du point proportionnelle au nombre de cadences evitees,
            rouge = mineur.
    right : moyenne jeune (4 premieres) vs vieux (4 dernieres).

If no work has a resolved PAC yet, it prints a message and exits cleanly --
so it is safe to run at any time (plug-and-play once the data lands).

Run:  .venv/bin/python plot_pac.py
"""
import csv
import statistics
import matplotlib.pyplot as plt

plt.rcParams.update({
    "figure.dpi": 150, "savefig.dpi": 150,
    "font.size": 11, "axes.titlesize": 13, "axes.titleweight": "bold",
    "axes.grid": True, "grid.alpha": 0.3, "axes.spines.top": False,
    "axes.spines.right": False,
})
MAJ, MIN, DARK = "#2c6fbb", "#c0392b", "#1a1a2e"


def num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    data = []
    for r in csv.DictReader(open("pac_resolved.csv")):
        off = num(r.get("first_pac_offset_ql", ""))
        if off is None:
            continue
        data.append({
            "wid": r["work_id"].replace("/i", ""),
            "year": int(r["year"]) if r.get("year") else 0,
            "off": off,
            "evaded": num(r.get("n_evaded_before", "")) or 0,
            "minor": "minor" in (r.get("key_nominal", "") or ""),
        })

    if not data:
        print("Aucune CP resolue dans pac_resolved.csv.")
        print("-> Remplir pac_annotations.csv, lancer resolve_annotations.py, puis relancer ceci.")
        return

    data.sort(key=lambda d: d["year"])
    xs = [d["year"] for d in data]
    ys = [d["off"] for d in data]
    colors = [MIN if d["minor"] else MAJ for d in data]
    sizes = [90 + 70 * d["evaded"] for d in data]

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), gridspec_kw={"width_ratios": [1.6, 1]})

    # --- left: temps jusqu'a la 1re CP au fil du temps ---
    ax1.plot(xs, ys, color="#999", lw=1, alpha=0.5, zorder=1)
    ax1.scatter(xs, ys, s=sizes, c=colors, edgecolor="white", linewidth=1.4, zorder=3)
    for d in data:
        ax1.annotate(d["wid"], (d["year"], d["off"]), xytext=(0, 10),
                     textcoords="offset points", ha="center", fontsize=8.5)
    ax1.set_xlabel("Annee de composition")
    ax1.set_ylabel("Temps jusqu'a la 1re CP (en noires)")
    ax1.set_title("Temps jusqu'a la premiere cadence parfaite")
    handles = [plt.Line2D([], [], marker="o", ls="", color=MAJ, label="Majeur"),
               plt.Line2D([], [], marker="o", ls="", color=MIN, label="Mineur")]
    ax1.legend(handles=handles, frameon=False, fontsize=9, loc="upper left")
    ax1.text(0.5, -0.18, "taille du point ∝ nombre de cadences evitees avant la CP",
             transform=ax1.transAxes, ha="center", fontsize=8.5, color="#777")

    # --- right: jeune vs vieux ---
    half = max(1, len(data) // 2)
    young, old = data[:half], data[half:]
    if young and old:
        ym = statistics.mean(d["off"] for d in young)
        om = statistics.mean(d["off"] for d in old)
        bars = ax2.bar(["Jeune\n(1res oeuvres)", "Vieux\n(dernieres)"], [ym, om],
                       color=[MAJ, DARK], width=0.6)
        for b, v in zip(bars, [ym, om]):
            ax2.annotate(f"{v:.1f}", (b.get_x() + b.get_width() / 2, v),
                         xytext=(0, 4), textcoords="offset points", ha="center", fontsize=11)
        ax2.set_ylabel("Temps moyen jusqu'a la 1re CP (noires)")
        ax2.set_title("Jeune vs vieux Mozart")
    else:
        ax2.axis("off")
        ax2.text(0.5, 0.5, "donnees partielles\n(remplir plus d'oeuvres)",
                 ha="center", va="center", fontsize=11, color="#777")

    fig.suptitle("Mozart : vers la cloture tonale au fil de la vie",
                 fontsize=15, fontweight="bold")
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    fig.savefig("fig_pac_timeline.png")
    print(f"-> fig_pac_timeline.png  ({len(data)}/8 oeuvres avec une CP resolue)")


if __name__ == "__main__":
    main()
