# Résumé de la démarche — projet Mozart (pour le diaporama)

> Points en vrac pour construire les diapositives. Raconte une *démarche de recherche* : un projet qui s'affine par essais, obstacles et corrections — ce qui est précisément l'esprit des humanités numériques.

## 1. Objectif initial (point de départ)
- Comparer **introductions et finales** de **16 œuvres pour piano solo** : 8 de Mozart, 8 de Brahms.
- Traits analysés : cadences, longueur de phrases, tonalités, type de mouvement (conjoint / disjoint), ambitus, *Stufen* (analyse schenkérienne).
- Outils envisagés : music21, jeu de données PDMX, MusicXML → MEI, MIDI → audio, Google Colab, Google Slides.

## 2. Premiers obstacles (les données)
- **Le dossier PDMX cloné ne contenait que le *code*, pas les partitions.** Le jeu de données réel (~250 000 partitions) a dû être téléchargé séparément depuis Zenodo.
- Le script `pdmx.py` n'est pas un *chargeur* : c'est le script de *création* du corpus, codé en dur pour le serveur des auteurs — inutilisable tel quel.
- **Le fichier `.csv` ne contient pas de colonne « instrument » lisible.** L'information instrumentale est encodée :
  - dans la colonne `tracks` (numéros de programme MIDI : `0` = piano seul, `0-0` = duo de pianos) ;
  - et, en clair, dans les fichiers JSON de métadonnées (`data.score.instrumentations`).
- Mise en place d'un environnement Python local (`venv` : pandas, music21, matplotlib).

## 3. Filtrage du corpus
- Sur **254 077 partitions** : **169 candidates Mozart** piano solo contre seulement **36 Brahms** — dont beaucoup d'arrangements, d'exercices ou de fragments.
- Constat : le matériel Brahms était nettement plus faible et bruité.

## 4. Volte-face décisive : abandon de Brahms
- Décision de **se concentrer uniquement sur Mozart**.
- Raisons :
  - les données Mozart sont abondantes et propres ;
  - une comparaison Mozart/Brahms risquait de produire un lieu commun (« Brahms = plus chromatique ») ;
  - une étude *intra-compositeur* est une question plus originale et plus maîtrisable.

## 5. Affinement de l'unité d'analyse
- Abandon des « 8–16 premières mesures » (frontière arbitraire).
- Nouvelle unité : **du début du premier mouvement jusqu'à la première cadence parfaite (CP / PAC)** dans le ton principal.
- C'est une **frontière théoriquement fondée** (premier point de clôture tonale), bien plus défendable.

## 6. Nouvel axe : une chronologie (jeune Mozart vs vieux Mozart)
- Idée ajoutée : afficher chaque trait **en fonction de la date de composition**.
- PDMX n'a pas de date de composition → **le numéro de Köchel sert d'axe chronologique** (le catalogue K. est ordonné dans le temps).
- Sélection de **8 premiers mouvements de sonates étalés de 1775 à 1789** (de la Sonate nº 1 K.279 à la dernière, K.576).

## 7. Réflexion méthodologique (le cœur « humanités numériques »)
- **La détection automatique des cadences est peu fiable** (music21 se trompe, surtout sur des transcriptions amateurs).
- Choix assumé d'un dispositif **« humain dans la boucle »** :
  - l'ordinateur *propose* des candidates de cadences et mesure l'objectif (ambitus, intervalles, tonalité…) ;
  - l'humain *tranche* sur la première CP et **consigne sa décision comme une donnée** (fichier d'annotations avec justification).
- Étude bonus possible : mesurer le **taux d'accord** entre les cadences détectées automatiquement et nos annotations manuelles.

## 8. Un piège technique repéré (et évité)
- **La mesure (« bar ») n'est pas une unité comparable** : un mouvement à 2/4 a deux fois plus de mesures qu'un mouvement à 4/4 pour une même durée → compter en mesures fausserait la chronologie.
- **L'anacrouse** (levée) décale la numérotation des mesures (music21 numérote la levée « mesure 0 »).
- Solution : enregistrer la position de la CP en **durée (noires / `offset_ql`)** depuis le début — indépendant du mètre et de l'anacrouse.
- Ajout d'une règle de repli : **si aucune CP avant la mesure 24, on retient la cadence imparfaite (CI / IAC) la plus forte.**

## 9. Hygiène des données
- Séparation stricte entre :
  - données *générées* par script (réécrites à chaque exécution) ;
  - données *saisies à la main* (annotations) — dans leur propre fichier, jamais écrasées.
- Liaison par une clé stable (le chemin/hachage du fichier `.mxl`), pas par le titre (trop hétérogène).

## 10. Résultats préliminaires (automatiques)
- **Mètres très variés** : 4/4, 2/4, 3/4, 6/8 — ce qui valide le choix de mesurer en durée et non en mesures.
- **K.576 (sa dernière sonate, 1789) est la seule avec une anacrouse** — justifie l'attention portée à la levée.
- **K.310 (la min, 1778) : seule ouverture à mouvement disjoint** (sauts dominants) — cohérent avec son caractère dramatique.
- **Les deux œuvres en mineur (K.310, K.457) repoussent la clôture** : pas de CP nette tôt → repli sur une CI. Piste interprétative intéressante.
- **K.457 : la tonalité détectée automatiquement est fausse** (mi♭ majeur au lieu de do mineur — confusion avec le relatif majeur) → bel exemple des limites de l'outil.

## 11. Limites à assumer dans l'exposé
- Échantillon réduit (n = 8) : tendances *illustratives*, non statistiquement robustes.
- Partitions PDMX = transcriptions d'amateurs → bruit possible (voicing, enharmonie).
- Les propositions automatiques de cadences sont volontairement « trop généreuses » → le tri humain est indispensable.

## 12. Livrables
- `corpus.csv` (les 8 œuvres, chemins stables) · `features_auto.csv` (traits objectifs) · `cadence_candidates.csv` (candidates de cadences) · `pac_annotations.csv` (jugements humains).
- Diaporama Google Slides : chronologie des traits, cycle des quintes, exemples sonores (MP3), réductions schenkériennes (lecture simultanée jeune/vieux).
