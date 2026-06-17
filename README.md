
# Chess FC

**Chess FC** est un jeu de stratégie qui mélange échecs et foot. Une description du jeu et des règles est disponible sur le site de Smart Games : https://playroom.smartgames.com/fr/games/chessfc.

Chaque joueur commence avec 6 pièces : 3 pions, une tour, un fou et un cavalier. Les règles de déplacement et de prises sont les mêmes qu'aux échecs. Une balle est placée au milieu du terrain. Si une pièce est sur la case de la balle, elle ne se déplace pas, mais à la place elle envoie la balle vers les cases accessibles normalement par cette pièce. La première équipe à marquer un but gagne le match.

Quelques règles à prendre en compte :

- les passes en diagonale par le pion sont possibles (seulement si une pièce est en diagonale) ;
- la prise en passant est à prendre en compte ;
- la promotion du pion en dame est à prendre en compte.

Ce projet implémente un moteur de règles complet, une intelligence artificielle basée sur alpha-beta, un mode local pour tester sans serveur, et une adaptation au serveur fourni en V3.

## Lancer une partie

### Mode local

Pour jouer ou tester sans serveur :

```bash
python main_local.py
```

Ce mode propose :
- humain contre humain ;
- humain contre IA ;
- IA contre humain ;
- IA contre IA.

Un coup s'écrit sous la forme `départ arrivée`, par exemple :

```text
B3 D3
```

On peut entrer `Q` pour quitter une partie locale.

### Mode serveur V3

Pour connecter l'IA au serveur :

```bash
python main.py 127.0.0.1 8080 nom-du-joueur
```

Exemple :

```bash
python main.py 127.0.0.1 8080 jad-test
```

 - 127.0.0.1 = adresse du serveur
 - 8080 = port 

Le fichier `main.py` est le vrai point d'entrée pour le serveur. Il utilise les callbacks de la bibliothèque `chessfc` V3.

## Organisation du code

| Fichier | Rôle |
|---|---|
| `constantes.py` | Couleurs, pièces, géométrie du plateau et constantes générales |
| `plateau.py` | Construction du plateau, coordonnées, accès aux cases |
| `regles.py` | Légalité et application des coups : déplacements, prises, passes, promotion, en passant |
| `ia.py` | Intelligence artificielle : évaluation, alpha-beta, tri des coups, transpositions |
| `zobrist.py` | Hachage de Zobrist pour identifier rapidement les positions |
| `adaptateur.py` | Conversion entre le format serveur V3 et notre format interne |
| `affichage.py` | Affichage texte du plateau |
| `main_local.py` | Boucle de jeu locale |
| `main.py` | Connexion au serveur V3 via les callbacks |
| `chessfc/` | Bibliothèque fournie pour communiquer avec le serveur |

Le sens général des dépendances est le suivant :

```text
constantes -> plateau -> regles / affichage -> ia -> main_local / main
```

`adaptateur.py` sert de couche intermédiaire entre le serveur et notre moteur.

## Représentation

### Plateau

Le plateau est représenté par une structure :

```python
list[list[int]]
```

Il contient 7 lignes et 9 colonnes. Les cases hors du plateau valent `MUR`, les cases jouables vides valent `VIDE`, et les pièces sont représentées par des entiers.

Par exemple :

```python
BTOUR = 6
```

représente une tour blanche.

La forme particulière du plateau est gérée avec la fonction `colonnes_jouables`, qui indique quelles colonnes existent réellement pour chaque ligne.

### Ballon

`BALLE` peut être posé sur le plateau, mais la position de la balle est aussi suivie dans une variable `balle` à part.

Ce choix est nécessaire car une pièce peut se tenir sur le ballon. Une seule case ne peut pas contenir proprement à la fois une pièce et la balle si on utilise uniquement une valeur entière dans le plateau.

### Coordonnées

Les coordonnées internes sont de la forme :

```python
(ligne, colonne)
```

Elles sont indexées à partir de 0.

La conversion depuis et vers la notation lisible, comme `"E4"`, est faite avec :

```python
recherche_nom
get_nom
```

### État de partie

Un état complet est représenté par :

```python
[plateau, balle, joueur, en_passant]
```

avec :
- `plateau` : position des pièces ;
- `balle` : position actuelle de la balle ;
- `joueur` : joueur au trait ;
- `en_passant` : case éventuelle permettant une prise en passant.

## Règles implémentées

Le moteur de règles gère :
- les déplacements classiques des pièces ;
- les captures ;
- les passes et tirs avec la balle ;
- les passes diagonales du pion ;
- la promotion du pion en dame ;
- la prise en passant ;
- les buts ;
- le pat ;
- les répétitions de position.

La génération des coups légaux est centralisée dans :

```python
coups_legaux(etat)
```

## Adaptation au serveur V3

La V3 du serveur utilise un objet `State` contenant le plateau, le joueur courant, la balle et d'autres informations de partie.

Notre moteur utilise une représentation plus simple. Le fichier `adaptateur.py` convertit donc :
- les pièces du serveur vers nos constantes ;
- les coordonnées serveur vers nos coordonnées internes ;
- nos coups internes vers des objets `Action` compréhensibles par le serveur.

Cela permet de garder le moteur de règles et l'IA indépendants du protocole serveur.

## Intelligence artificielle

L'IA est dans `ia.py`.

Elle repose sur un algorithme **minimax avec élagage alpha-beta**.

Les Blancs maximisent le score, tandis que les Noirs le minimisent. Les positions terminales sont fortement valorisées pour favoriser les victoires rapides et éviter les défaites proches.

## Fonction d'évaluation

La fonction d'évaluation prend en compte :
- la valeur matérielle des pièces ;
- la progression de la balle vers le but adverse ;
- le contrôle de la balle ;
- la proximité de la balle avec le but.

Les valeurs matérielles sont inspirées des échecs :
- pion : 1 ;
- cavalier : 3 ;
- fou : 3 ;
- tour : 5 ;
- dame : 9.

Le score est positif si la position est favorable aux Blancs, et négatif si elle est favorable aux Noirs.

## Optimisations de l'IA

Plusieurs optimisations sont utilisées :
- tri des coups avant la recherche ;
- table de transposition ;
- hachage de Zobrist ;
- détection des répétitions ;
- choix aléatoire entre coups équivalents.

Le tri des coups donne la priorité aux coups prometteurs :
- tirs ou passes vers le but ;
- buts immédiats ;
- captures ;
- promotions ;
- progression vers le camp adverse.

Cela permet à alpha-beta de couper plus rapidement certaines branches.

## Hachage de Zobrist

Le fichier `zobrist.py` associe des clés aléatoires aux pièces, aux cases, à la balle, au joueur courant et à la case éventuelle d'en passant.

Le hash obtenu sert à :
- détecter les répétitions ;
- reconnaître rapidement une position déjà analysée ;
- alimenter la table de transposition.

## Branche `test-ia`

La branche `test-ia` contient des outils pour comparer plusieurs versions de l'IA.

Elle permet notamment de faire jouer une nouvelle IA contre une ancienne IA afin de tester différentes techniques de scoring, différentes profondeurs de recherche et différentes heuristiques.

Le fichier principal est :

```bash
python duel_ia.py
```

Il lance plusieurs matchs, alterne les couleurs, puis affiche :
- les victoires de la nouvelle IA ;
- les victoires de l'ancienne IA ;
- les matchs nuls.

Cette branche nous a permis de comparer les modifications de manière plus objective avant de les garder dans la version principale.

## Points forts

Les points forts du projet sont :
- séparation claire entre règles, IA, affichage et serveur ;
- mode local pratique pour tester rapidement ;
- adaptation au serveur V3 ;
- IA basée sur alpha-beta ;
- table de transposition ;
- hachage de Zobrist ;
- gestion des règles spécifiques comme la promotion et l'en passant ;
- branche dédiée aux tests comparatifs d'IA.

## Limites

Les principales limites sont :
- la fonction d'évaluation reste heuristique ;
- les poids de scoring peuvent encore être améliorés ;
- la profondeur de recherche est limitée par le temps de calcul ;
- IA contre IA identique mène souvent à des matchs nuls, car les décisions sont symétriques ou déterministes ;
- certaines positions complexes de fin de partie peuvent encore être mieux évaluées.

## Répartition du travail

Nous avons travaillé ensemble pendant toute la durée du projet. Les choix d'implémentation, la structure du code, les règles, l'adaptation au serveur V3, les tests locaux, les améliorations de l'IA et les comparaisons entre versions ont été faits en binôme.

La répartition est donc équilibrée :

| Membre | Répartition |
|---|---|
| Jad | 50 % |
| Quentin | 50 % |

Les commits du dépôt témoignent de cette collaboration continue.
