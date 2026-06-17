"""Hachage de Zobrist des états du jeu."""

import random

from constantes import *

SEED = 256
rdgen = random.Random(SEED)

# une clé pour chaque pièce sur chaque case possible
CLES_PIECES = {
    (l, c): {piece: rdgen.getrandbits(64) for piece in PIECES}
    for l in range(NB_LIGNES)
    for c in range(NB_COLONNES)
}

# une clé par case possible pour la balle
CLES_BALLE = {
    (l, c): rdgen.getrandbits(64)
    for l in range(NB_LIGNES)
    for c in range(NB_COLONNES)
}

# une clé pour le joueur (tour aux noirs ou blancs)
CLE_JOUEUR = rdgen.getrandbits(64)

# une clé par case cible d'en passant
CLES_EN_PASSANT = {
    (l, c): rdgen.getrandbits(64)
    for l in range(NB_LIGNES)
    for c in range(NB_COLONNES)
}

def zobrist_hash(etat: list) -> int:
    plateau, balle, joueur, en_passant = etat
    h = 0

    # pièces présentes sur le plateau (VIDE et MUR sont ignorés)
    for l in range(NB_LIGNES):
        for c in range(NB_COLONNES):
            piece = plateau[l][c]
            if piece in PIECES:
                h ^= CLES_PIECES[(l, c)][piece]

    # position de la balle
    h ^= CLES_BALLE[balle]

    # joueur
    if joueur == NOIR:
        h ^= CLE_JOUEUR

    # case d'en passant éventuelle
    if en_passant is not None:
        h ^= CLES_EN_PASSANT[en_passant]

    return h
