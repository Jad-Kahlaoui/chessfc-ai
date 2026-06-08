from constantes import *
from plateau import get_piece, set_piece, get_couleur, est_atteignable


def chemin_libre(plateau: list[list[int]], case_src: tuple[int, int], case_dst: tuple[int, int]) -> bool:
    # direction
    dl = case_dst[0] - case_src[0]
    dc = case_dst[1] - case_src[1]
    dir_l = (dl > 0) - (dl < 0)
    dir_c = (dc > 0) - (dc < 0)

    # vérification pas à pas des cases strictement entre src et dst
    l, c = case_src[0] + dir_l, case_src[1] + dir_c
    while (l, c) != case_dst:
        if plateau[l][c] != VIDE:
            return False
        l += dir_l
        c += dir_c

    return True

def est_jouable(plateau: list[list[int]], case_src: tuple[int, int], case_dst: tuple[int, int]) -> bool:
    if case_src == case_dst: # pas de coup sur place
        return False

    piece = get_piece(plateau, case_src)

    # vérification de la piece
    if piece not in PIECES: # case de départ vide / mur
        return False

    # vérification de la case
    if not est_atteignable(case_dst[0], case_dst[1]):
        return False

    # vérification de la couleur
    couleur = get_couleur(piece)
    piece_cible = get_piece(plateau, case_dst)
    if piece_cible in PIECES and get_couleur(piece_cible) == couleur:
        return False  # on ne prend pas une de ses propres pièces

    # déplacement
    dl = case_dst[0] - case_src[0]
    dc = case_dst[1] - case_src[1]

    # cavalier
    if piece in (BCAVA, NCAVA):
        return (abs(dl), abs(dc)) in ((1, 2), (2, 1))

    # tour
    if piece in (BTOUR, NTOUR):
        return (dl == 0 or dc == 0) and chemin_libre(plateau, case_src, case_dst)

    # fou
    if piece in (BFOU, NFOU):
        return abs(dl) == abs(dc) and chemin_libre(plateau, case_src, case_dst)

    # pion
    if piece in (BPION, NPION):
        sens = 1 if couleur == BLANC else -1 # avance vers le camp adverse

        # prise en diagonale
        if dc == sens and abs(dl) == 1:
            return piece_cible != VIDE  # adverse ou ballon

        # avance tout droit
        if dl == 0 and piece_cible == VIDE:
            if (case_src[1] == 1 and couleur == BLANC) or (case_src[1] == 7 and couleur == NOIR):
                return dc in (sens, 2 * sens) and chemin_libre(plateau, case_src, case_dst)
            return dc == sens and chemin_libre(plateau, case_src, case_dst)

    return False

def passe_jouable(plateau: list[list[int]], balle: tuple[int, int], case_dst: tuple[int, int]) -> bool:
    if case_dst == balle: # le ballon doit se déplacer
        return False
    if not est_atteignable(case_dst[0], case_dst[1]):
        return False

    piece = get_piece(plateau, balle) # la pièce qui possède le ballon
    if piece not in PIECES:
        return False

    couleur = get_couleur(piece)
    dl = case_dst[0] - balle[0]
    dc = case_dst[1] - balle[1]

    # cavalier
    if piece in (BCAVA, NCAVA):
        return (abs(dl), abs(dc)) in ((1, 2), (2, 1))

    # tour
    if piece in (BTOUR, NTOUR):
        return (dl == 0 or dc == 0) and chemin_libre(plateau, balle, case_dst)

    # fou
    if piece in (BFOU, NFOU):
        return abs(dl) == abs(dc) and chemin_libre(plateau, balle, case_dst)

    # pion
    if piece in (BPION, NPION):
        sens = 1 if couleur == BLANC else -1

        # diagonale
        if dc == sens and abs(dl) == 1:
            return True

        # tout droit
        if dl == 0:
            if (balle[1] == 1 and couleur == BLANC) or (balle[1] == 7 and couleur == NOIR):
                return dc in (sens, 2 * sens) and chemin_libre(plateau, balle, case_dst)
            return dc == sens and chemin_libre(plateau, balle, case_dst)

    return False

def deplacement(plateau: list[list[int]], case_src: tuple[int, int], case_dst: tuple[int, int]) -> None:
    piece_src = get_piece(plateau, case_src)
    set_piece(plateau, case_dst, piece_src)
    set_piece(plateau, case_src, VIDE)

    return None

def jouer(plateau: list[list[int]], balle: tuple[int, int], case_src: tuple[int, int], case_dst: tuple[int, int]) -> tuple[int, int]:

    # frappe du ballon
    if case_src == balle:
        if get_piece(plateau, case_dst) == VIDE:
            set_piece(plateau, case_dst, BALLE)
        return case_dst

    # déplacement de la pièce
    deplacement(plateau, case_src, case_dst)

    return balle
