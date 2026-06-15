from constantes import *


def colonnes_jouables(l: int) -> tuple[int, int]:
    if 2 <= l <= 4:
        return (0, NB_COLONNES)
    if l in (0, 1, 5, 6):
        return (2, 7)
    return (0, 0)


def est_atteignable(l: int, c: int) -> bool:
    if not 0 <= l < NB_LIGNES:
        return False
    deb, fin = colonnes_jouables(l)
    return deb <= c < fin

def get_nom(case: tuple[int, int]) -> str:
    l, c = case
    return f"{chr(ord('A') + c)}{l + 1}"

def recherche_nom(nom_case: str) -> tuple[int, int]:
    # vérification du nom reçu
    if len(nom_case) < 2 or nom_case[0] not in ALPHA or not nom_case[1:].isdigit():
        raise ValueError(f"Coordonnée invalide : {nom_case}")

    # affectation
    c = ALPHA[nom_case[0]]
    l = int(nom_case[1:]) - 1

    # vérification que la case existe
    if not est_atteignable(l, c):
        raise ValueError(f"Case hors plateau : {nom_case}")

    return (l, c)

def plateau_vide() -> Plateau:
    plateau = [[MUR] * NB_COLONNES for _ in range(NB_LIGNES)]
    for l in range(NB_LIGNES):
        deb, fin = colonnes_jouables(l)
        for c in range(deb, fin):
            plateau[l][c] = VIDE
    return plateau

def plateau_init() -> Plateau:
    plateau = plateau_vide()
    plateau[2][0] = BTOUR
    plateau[3][0] = BFOU
    plateau[4][0] = BCAVA
    plateau[2][1] = BPION
    plateau[3][1] = BPION
    plateau[4][1] = BPION
    plateau[2][8] = NCAVA
    plateau[3][8] = NFOU
    plateau[4][8] = NTOUR
    plateau[2][7] = NPION
    plateau[3][7] = NPION
    plateau[4][7] = NPION
    set_piece(plateau, INIT_BALLE, BALLE)
    return plateau

def get_piece(plateau: Plateau, case:tuple[int, int]) -> int:
    l, c = case
    return plateau[l][c]

def set_piece(plateau: Plateau, case:tuple[int, int], valeur: int) -> None:
    l, c = case
    plateau[l][c] = valeur

def get_couleur(piece: int) -> int:
    if piece in (BPION, BCAVA, BFOU, BTOUR, BDAME):
        return BLANC
    elif piece in (NPION, NCAVA, NFOU, NTOUR, NDAME):
        return NOIR
    else:
        raise ValueError(f"Pièce invalide : {piece}")
