# Couleurs / joueurs
BLANC = 0
NOIR = 1

# Contenu de case spécial
VIDE = 0  # case vide mais jouable
MUR = 1  # case hors du terrain
BALLE = 2

# Types de pièces
BPION = 3
BCAVA = 4
BFOU = 5
BTOUR = 6

NPION = 7
NCAVA = 8
NFOU = 9
NTOUR = 10

BDAME = 11
NDAME = 12

PIECES = (3, 4, 5, 6, 7, 8, 9, 10, 11, 12)

# Géométrie du plateau
ALPHA = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8}
NB_LIGNES = 7
NB_COLONNES = 9
INIT_BALLE = (3, 4)

# Types
Case = tuple[int, int]
