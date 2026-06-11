- Contexte :  École d’été en humanités numériques (universitaire), projet en équipe de trois musicologues  
- Équipe : Leo McFadden, Ali Said Achimo, Thibault Daraignès  
- Timeline : Quelques heures (pour le terminer) — donc il faut que la portée du projet soit adaptée à cela.  
- Objectifs : comparer les introductions et les finaux d’un échantillon de 16 oeuvres musicales pour piano solo de Brahms et Mozart, dont 8 de Mozart et 8 de Brahms.  
   

- Approche envisagée   
  - S’appuyer sur le format musicxml   
  - Annoter quelques éléments qui nous intéressent   
    - Dans un premier temps, analyse par l’ordinateur (music21) : sélectionner les ouvertures des morceaux   
    - Dans un second temps, corriger les fautes  « à la main », puis créer un script avec l’IA pour peaufiner les données.

    \-Élément recherchés : cadences, longueur de phrases, tonalités, nature de mouvement (linéaire—avec le mouvement par étape—ou segmenté — mouvement par sauts), ambitus, les stufen (de l’analyse schenkérienne)  

\- Outils envisagés (pas obligatoires — tu peux nous conseiller un autre) 

- Music21 python  
- PDMX dataset (pour les morceaux)  : il y  a un fichier .csv et nous allons chercher dans cette base les morceaux pour piano solo de Mozart et Brahms spécifiquement.  
- Un outil pour passer de MusicXML à MEI (ou tout simplement un conseil pour le faire, car MusicXML et MEI sont compatibles)  
- Quelque chose pour convertir les fichiers midi en format compatible avec powerpoint   
- Google notebook (on n’est pas encore décidé—certains d’entre nous préfèrent travailler en mode « local », mais le cours (à but pédagogique) encourage google Colab (sans l’imposer), quel est ton avis dans notre cas ?   
- Google slides (pour le diaporama) 


## **Et après…**

- Étant donné la nature de notre corpus, nous pensons qu’il serait préférable de présenter un powerpoint avec les exemples musicaux sonores et présentés sur des partitions musicales correspondant aux objectifs et les résultats auxquels nous avons abouti.   
  - À cet égard, Google slides est peut-être l’outil de préférence dans ce cours, car le professeur nous demande de lui partager notre diaporama  
  - Compt tenu du type d’exposé demandé, il est nécessaire d’avoir un rendu qui affiche/présente les résultats de manière intéressant (par exemple, cartographier les différentes tonalités sur une graphique du cycle de quintes/quartes, jouer les réductions en stufen des deux (ou plusieurs morceaux comparés en même temps — pour écouter la différence). 

Nous voulons que tu nous fournisses un pipeline pour réaliser adéquatement ce projet, sachant que nous avons peu de temps.

## **Questions/ remarques…**

- Est-ce que c’est mieux d’ajouter les balises MEIs « à la main » ou y a-t-il un outil que tu nous conseilles ?   
- Qu’est ce que ton avis de notre workflow jusqu’à présent ? (Des choses à lesquelles nous n’avons pas pensé, des améliorations   
- Si tu as des questions, ou des précisions avant de commencer à travailler, n'hésite pas \!

