# Mozart, premiers mouvements : ouverture → première cadence parfaite

Étude de musicologie computationnelle (école d'été en humanités numériques).
Analyse de **8 premiers mouvements de sonates pour piano de Mozart**, étalés de 1775 à 1789,
de l'ouverture jusqu'à la **première cadence parfaite (CP / PAC)** dans le ton principal —
pour comparer les traits du *jeune* et du *vieux* Mozart.

**Équipe :** Leo McFadden · Ali Said Achimo · Thibault Daraignès

Le récit complet de la démarche (objectifs, obstacles, volte-face Brahms, méthodologie)
est dans [`resume_demarche.md`](resume_demarche.md). Le plan technique est dans
[`pipeline.md`](pipeline.md).

## Données

Les partitions proviennent de **PDMX** (Public Domain MusicXML), à télécharger depuis Zenodo :
<https://zenodo.org/records/15571083>. **Ce dépôt ne contient PAS les données** (~49 Go) —
elles sont à récupérer et à extraire dans un dossier `PDMX-lib/` à la racine.

## Installation

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

## Pipeline (à exécuter dans l'ordre)

| Script | Rôle | Sortie |
|---|---|---|
| `filter_corpus.py` | filtre l'index PDMX → candidates piano solo Mozart | `candidates_mozart.csv` |
| `extract_features.py` | mesures music21 (mètre, anacrouse, ambitus, mouvement) + propose les cadences | `features_auto.csv`, `cadence_candidates.csv` |
| `plot_features.py` | graphiques (chronologie + cycle des quintes) | `fig_timeline.png`, `fig_circle_of_fifths.png` |

```bash
.venv/bin/python filter_corpus.py
.venv/bin/python extract_features.py
.venv/bin/python plot_features.py
```

## Fichiers de données

- `corpus.csv` — les 8 œuvres choisies (work_id, **année**, tonalité, **titre**, chemins). Saisi à la main.
- `features_auto.csv` — traits objectifs extraits par music21 (total + main droite).
- `cadence_candidates.csv` — cadences V→I proposées (PAC / IAC) à valider.
- `pac_annotations.csv` — jugements humains sur la première CP (saisie manuelle, jamais écrasée).

## Méthodologie : humain dans la boucle

La détection automatique des cadences est peu fiable. Le dispositif retenu :
**l'ordinateur mesure et *propose* les cadences ; l'humain *tranche* sur la première CP**
et consigne sa décision comme une donnée (avec justification). La position est enregistrée
en **durée (`offset_ql`)** plutôt qu'en numéro de mesure, pour rester comparable malgré les
différences de mètre et la présence d'anacrouses.

## Citation des données

PDMX : Long, P., Novack, Z., Berg-Kirkpatrick, T., McAuley, J. (2025).
*PDMX: A Large-Scale Public Domain MusicXML Dataset for Symbolic Music Processing.* ICASSP 2025.
