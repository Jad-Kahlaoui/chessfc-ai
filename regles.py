"""Règles du jeu : génération et application des coups."""

from constantes import *
from plateau import get_piece, set_piece, get_couleur, est_atteignable, colonnes_jouables


def cases_visees(plateau: Plateau, case_src: Case) -> list[Case]:
    piece = get_piece(plateau, case_src)
    couleur = get_couleur(piece)
    l, c = case_src
    cases = []

    # cavalier
    if piece in (BCAVA, NCAVA):
        for dl, dc in ((1, 2), (2, 1), (-1, 2), (-2, 1), (1, -2), (2, -1), (-1, -2), (-2, -1)):
            if est_atteignable(l + dl, c + dc):
                cases.append((l + dl, c + dc))
        return cases

    # tour / fou / dame
    directions = []
    if piece in (BTOUR, NTOUR):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    elif piece in (BFOU, NFOU):
        directions = [(1, 1), (1, -1), (-1, 1), (-1, -1)]
    elif piece in (BDAME, NDAME):
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1), (1, 1), (1, -1), (-1, 1), (-1, -1)]

    if piece in (BTOUR, NTOUR, BFOU, NFOU, BDAME, NDAME):
        for dl, dc in directions: 
            nl, nc = l + dl, c + dc
            while est_atteignable(nl, nc):
                cases.append((nl, nc))
                if plateau[nl][nc] != VIDE: # obstacle
                    break
                nl += dl
                nc += dc 
        return cases

    # pion
    sens = 1 if couleur == BLANC else -1  # avance vers le camp adverse
    
    # prise diagonale
    for dl in (1, -1):
        if est_atteignable(l + dl, c + sens):
            cases.append((l + dl, c + sens))
    
    # tout droit
    if est_atteignable(l, c + sens) and plateau[l][c + sens] in (VIDE, BALLE):

        # avance simple
        cases.append((l, c + sens))

        # avance double au depart
        if ((c == 1 and couleur == BLANC) or (c == 7 and couleur == NOIR)) and est_atteignable(l, c + 2 * sens) and plateau[l][c + 2 * sens] == VIDE:
            cases.append((l, c + 2 * sens))

    return cases

def est_jouable(plateau: Plateau, case_src: Case, case_dst: Case, en_passant: Case | None = None) -> bool:
    piece = get_piece(plateau, case_src)

    # verification de la pièce
    if piece not in PIECES:
        return False
    
    # vérification de la case
    if case_dst not in cases_visees(plateau, case_src):
        return False

    # vérification de la cible
    cible = get_piece(plateau, case_dst)
    if cible in PIECES and get_couleur(cible) == get_couleur(piece):
        return False  # on ne prend pas une de ses propres pièces
    if piece in (BPION, NPION) and case_dst[0] != case_src[0] and cible == VIDE:
        if case_dst == en_passant:
            return True
        return False  # le pion ne prend en diagonale que sur une cible

    return True

def cases_passe(plateau: Plateau, balle: Case) -> list[Case]:
    # cases vers lesquelles la pièce sur la balle peut l'envoyer
    piece = get_piece(plateau, balle)
    if piece not in (BPION, NPION):
        return cases_visees(plateau, balle)

    # le pion vise sa case avant (occupée ou non) et ses deux diagonales avant
    l, c = balle
    sens = 1 if get_couleur(piece) == BLANC else -1
    cases = []
    for dl in (0, 1, -1):
        if est_atteignable(l + dl, c + sens):
            cases.append((l + dl, c + sens))
    return cases

def passe_jouable(plateau: Plateau, balle: Case, case_dst: Case) -> bool:
    piece = get_piece(plateau, balle)  # la pièce qui possède le ballon
    if piece not in PIECES:
        return False
    if case_dst not in cases_passe(plateau, balle):
        return False

    # le pion passe devant lui (case occupée ou non), mais en diagonale
    # uniquement sur une pièce (alliée ou adverse)
    if piece in (BPION, NPION) and case_dst[0] != balle[0]:
        return get_piece(plateau, case_dst) in PIECES

    return True

def deplacement(plateau: Plateau, case_src: Case, case_dst: Case) -> None:
    piece_src = get_piece(plateau, case_src)
    set_piece(plateau, case_dst, piece_src)
    set_piece(plateau, case_src, VIDE)

def jouer(plateau: Plateau, balle: Case, case_src: Case, case_dst: Case,
            en_passant: Case | None = None) -> tuple[Case, Case | None]:

    # frappe du ballon
    if case_src == balle:
        if get_piece(plateau, case_dst) == VIDE:
            set_piece(plateau, case_dst, BALLE)
        return case_dst, None

    # prise en passant 
    piece = get_piece(plateau, case_src)
    if piece in (BPION, NPION) and case_dst == en_passant:
        set_piece(plateau, (case_dst[0], case_src[1]), VIDE) ## manger le pion adverse

    # déplacement de la pièce
    deplacement(plateau, case_src, case_dst)

    # promotion d'un pion à une dame
    if piece == BPION and case_dst[1] == NB_COLONNES - 2:
        set_piece(plateau, case_dst, BDAME)

    elif piece == NPION and case_dst[1] == 1:
        set_piece(plateau, case_dst, NDAME)

    nouveau_ep: Case | None = None
    if piece in (BPION, NPION) and abs(case_dst[1] - case_src[1]) == 2:
        nouveau_ep = (case_src[0], (case_src[1] + case_dst[1]) //2 )
    
    return balle, nouveau_ep

def get_etat(plateau: Plateau, balle: Case, joueur: int, en_passant: Case | None = None) -> list:
    return [plateau, balle, joueur, en_passant]

def coups_legaux(etat: list) -> list[tuple[Case, Case]]:
    plateau, balle, joueur, en_passant = etat
    coups = []

    for l in range(NB_LIGNES):
        deb_col, fin_col = colonnes_jouables(l)
        for c in range(deb_col, fin_col):
            case_src = (l, c)
            piece = get_piece(plateau, case_src)
            if piece not in PIECES or get_couleur(piece) != joueur:
                continue
            
            # frappe du ballon
            if case_src == balle:
                for case_dst in cases_passe(plateau, case_src):
                    if passe_jouable(plateau, balle, case_dst):
                        coups.append((case_src, case_dst))
            # déplacement
            else:
                for case_dst in cases_visees(plateau, case_src):
                    if est_jouable(plateau, case_src, case_dst, en_passant):
                        coups.append((case_src, case_dst))

    return coups

def final(etat: list, coups: list | None = None) -> int | None:
    _, balle, _, _ = etat

    # but dans les cages blanches
    if balle[1] in (0, 1):
        return -1

    # but dans les cages noires
    if balle[1] in (7, 8):
        return 1

    # pat : l'appelant peut fournir coups_legaux déjà calculé pour éviter un recalcul
    if coups is None:
        coups = coups_legaux(etat)
    if coups == []:
        return 0

    return None

