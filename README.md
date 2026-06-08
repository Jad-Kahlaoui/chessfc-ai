# Chess FC

**Chess FC** est un jeu de stratégie qui mélange échecs et foot. Une description du jeu et des règles est disponible sur le site de Smart Games : https://playroom.smartgames.com/fr/games/chessfc.
Chaque joueur commence avec 6 pièces (3 pions, une tour, un fou et un cavalier). Les règles de déplacement et de prises sont les mêmes qu'aux échecs. Une balle est placée au milieu du terrain. Si une pièce est sur la case de la balle, elle ne se déplace pas, mais à la place envoie la balle vers les cases accessibles normalement à la pièce. La première équipe à marquer un but gagne le match.

Quelques règles à prendre en compte :
- Les passes en diagonale par le pion sont possibles
- La prise en passant est à prendre en compte
- La promotion du pion (en dame) est à prendre en compte

## Lancer une partie

```bash
python chessfc\main.py
```

Partie humain contre humain au clavier. Un coup s'écrit `départ arrivée`
(ex. `B3 D3`) ; `Q` pour quitter.

## Organisation du code

| Fichier | Rôle |
|---|---|
| `constantes.py` | couleurs, pièces, géométrie du plateau |
| `plateau.py` | construction du plateau, coordonnées, accès aux cases |
| `regles.py` | légalité et application des coups (déplacements, frappe du ballon) |
| `affichage.py` | affichage du plateau |
| `main.py` | boucle de jeu |

Le sens des dépendances est le suivant : `constantes → plateau → regles / affichage → main`.

## Représentation

- **Plateau** : `list[list[int]]` de 7 lignes × 9 colonnes. Les cases hors du plateau valent `MUR`, sinon valent `VIDE` ou une pièce. Une pièce est un entier, ex. `BTOUR` = 6 (tour blanche).
- **Ballon** : `BALLE` est posé sur le plateau, mais sa position est aussi suivie dans une variable `balle` à part — car une pièce peut se tenir **sur** le ballon, et une case ne peut pas contenir les deux à la fois.
- **Coordonnées** : `(ligne, colonne)` indexées à partir de 0 ; conversion depuis/vers la notation `"E4"` via `recherche_nom` / `get_nom`.
