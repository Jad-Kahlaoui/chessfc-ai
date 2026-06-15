from constantes import *
from plateau import get_piece, get_couleur

# Symboles d'affichage 
GLYPHS = {
    VIDE: " ",
    BPION: "♟",
    BCAVA: "♞",
    BFOU: "♝",
    BTOUR: "♜",
    BDAME: "♛",
    NPION: "♙",
    NCAVA: "♘",
    NFOU: "♗",
    NTOUR: "♖",
    NDAME: "♕",
    BALLE: "o"
}

def glyphe_case(plateau: list[list[int]], balle: tuple[int, int], l: int, c: int) -> str:
    piece = get_piece(plateau, (l, c))

    # case sans pièce
    if piece not in PIECES:
        return " o " if (l, c) == balle else "   "

    # case avec pièce
    glyphe = GLYPHS[piece] + " "
    marque = "o" if (l, c) == balle else " "

    # blanc collé à gauche, noir collé à droite (pieces sur deux largeurs)
    if get_couleur(piece) == BLANC:
        return glyphe + marque
    return marque + glyphe

def afficher(plateau:list[list[int]], balle: tuple[int, int]) -> None:
    marge = "  "  # colonne des numéros de ligne (1 chiffre + 1 espace)
    bordure_courte = marge + "    "*2 + "+---"*5+"+" + "\n"
    bordure_longue = marge + "+---"*9+"+" + "\n"

    str_plateau = ""

    # lignes du haut
    for l in range(0, 2):
        str_plateau += bordure_courte + f"{l+1} " + "    "*2
        for c in range(2, 7):
            str_plateau += "|" + glyphe_case(plateau, balle, l, c)
        str_plateau += "|\n"

    # lignes du milieu
    for l in range(2, 5):
        str_plateau += bordure_longue + f"{l+1} "
        for c in range(0, 9):
            str_plateau += "|" + glyphe_case(plateau, balle, l, c)
        str_plateau += "|\n"

    # lignes du bas
    str_plateau += bordure_longue
    for l in range(5, 7):
        str_plateau += f"{l+1} " + "    "*2
        for c in range(2, 7):
            str_plateau += "|" + glyphe_case(plateau, balle, l, c)
        str_plateau += "|\n" + bordure_courte

    # lettres des colonnes
    str_plateau += marge
    for c in range(NB_COLONNES):
        str_plateau += f"  {chr(ord('A') + c)} "
    str_plateau += "\n"

    print(str_plateau)
    return None
