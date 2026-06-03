# Couleurs / joueurs
WHITE = 0
BLACK = 1

# Contenu de case spécial
EMPTY = 0  # case vide mais jouable
WALL = 1  # case hors du terrain
BALLE = 2

# Types de pièces
WPAWN = 3
WKNIGHT = 4
WBISHOP = 5
WROOK = 6

BPAWN = 7
BKNIGHT = 8
BBISHOP = 9
BROOK = 10

PIECES = (3, 4, 5, 6, 7, 8, 9, 10)

# Symboles d'affichage (majuscule = Blancs, minuscule = Noirs)
GLYPHS = {
    EMPTY: " ",
    WPAWN: "P",
    WKNIGHT: "N",
    WBISHOP: "B",
    WROOK: "R",
    BPAWN: "p",
    BKNIGHT: "n",
    BBISHOP: "b",
    BROOK: "r",
    BALLE: "o"
}

# Géométrie du plateau
ALPHA = {"A": 0, "B": 1, "C": 2, "D": 3, "E": 4, "F": 5, "G": 6, "H": 7, "I": 8}
NB_LIGNES = 7
NB_COLONNES = 9
INIT_BALLE = (3, 4)


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

def plateau_vide() -> list[list[int]]:
    plateau = [[WALL] * NB_COLONNES for _ in range(NB_LIGNES)]
    for l in range(NB_LIGNES):
        deb, fin = colonnes_jouables(l)
        for c in range(deb, fin):
            plateau[l][c] = EMPTY
    return plateau


# Disposition initiale
def plateau_init() -> list[list[int]]:
    plateau = plateau_vide()
    plateau[2][0] = WROOK
    plateau[3][0] = WBISHOP
    plateau[4][0] = WKNIGHT
    plateau[2][1] = WPAWN
    plateau[3][1] = WPAWN
    plateau[4][1] = WPAWN
    plateau[2][8] = BKNIGHT
    plateau[3][8] = BBISHOP
    plateau[4][8] = BROOK
    plateau[2][7] = BPAWN
    plateau[3][7] = BPAWN
    plateau[4][7] = BPAWN
    plateau[INIT_BALLE[0]][INIT_BALLE[1]] = BALLE
    return plateau

def get_piece(plateau: list[list[int]], case:tuple[int, int]) -> int:
    l, c = case
    return plateau[l][c]

def get_couleur(piece: int) -> int:
    if piece in (WPAWN, WKNIGHT, WBISHOP, WROOK):
        return WHITE
    elif piece in (BPAWN, BKNIGHT, BBISHOP, BROOK):
        return BLACK
    else:
        raise ValueError(f"Pièce invalide : {piece}")

def chemin_libre(plateau: list[list[int]], case_src: tuple[int, int], case_dst: tuple[int, int]) -> bool:
    # direction
    dl = case_dst[0] - case_src[0]
    dc = case_dst[1] - case_src[1]
    dir_l = (dl > 0) - (dl < 0)
    dir_c = (dc > 0) - (dc < 0)

    # vérification pas à pas des cases strictement entre src et dst
    l, c = case_src[0] + dir_l, case_src[1] + dir_c
    while (l, c) != case_dst:
        if plateau[l][c] != EMPTY:
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
    
    couleur = get_couleur(piece)
    piece_cible = get_piece(plateau, case_dst)
    if piece_cible in PIECES and get_couleur(piece_cible) == couleur:
        return False  # on ne prend pas une de ses propres pièces

    # déplacement
    dl = case_dst[0] - case_src[0]
    dc = case_dst[1] - case_src[1]

    # cavalier
    if piece in (WKNIGHT, BKNIGHT):
        return (abs(dl), abs(dc)) in ((1, 2), (2, 1))

    # tour
    if piece in (WROOK, BROOK):
        return (dl == 0 or dc == 0) and chemin_libre(plateau, case_src, case_dst)

    # fou
    if piece in (WBISHOP, BBISHOP):
        return abs(dl) == abs(dc) and chemin_libre(plateau, case_src, case_dst)

    # pion
    if piece in (WPAWN, BPAWN):
        sens = 1 if couleur == WHITE else -1 # n'avance que vers le camp adverse

        if (case_src[1] == 1 and couleur == WHITE) or (case_src[1] == 7 and couleur == BLACK):
            return dl == 0 and dc in (sens, 2 * sens) and chemin_libre(plateau, case_src, case_dst)
        return dl == 0 and dc == sens and chemin_libre(plateau, case_src, case_dst)

    return False

def deplacement(plateau: list[list[int]], case_src: tuple[int, int], case_dst: tuple[int, int]) -> None:
    src_l, src_c = case_src
    dst_l, dst_c = case_dst

    plateau[dst_l][dst_c] = plateau[src_l][src_c]
    plateau[src_l][src_c] = EMPTY

# Affichage
def afficher(plateau:list[list[int]]) -> None:
    bordure_courte = "    "*2 + "+---"*5+"+" + "    "*2 + "\n"
    bordure_longue = "+---"*9+"+" + "\n"

    str_plateau = ""

    # lignes du haut
    for l in range(0, 2):
        str_plateau += bordure_courte + "    "*2
        for c in range(2, 7):
            str_plateau += "| " + GLYPHS[plateau[l][c]] + " "
        str_plateau += "|\n"

    # lignes du milieu
    for l in range(2, 5):
        str_plateau += bordure_longue
        for c in range(0, 9):
            str_plateau += "| " + GLYPHS[plateau[l][c]] + " "
        str_plateau += "|\n"

    # lignes du bas
    str_plateau += bordure_longue
    for l in range(5, 7):
        str_plateau += "    "*2
        for c in range(2, 7):
            str_plateau += "| " + GLYPHS[plateau[l][c]] + " "
        str_plateau += "|\n" + bordure_courte

    print(str_plateau)
    return None


# Boucle de jeu
def play() -> None:
    plateau = plateau_init()
    to_move = WHITE
    
    while True:

        # détermine à qui de jouer
        if to_move == 0:
            couleur_coup = "Blancs"
        else :
            couleur_coup = "Noirs"

        # affichage du plateau
        afficher(plateau)

        # saisie utilisateur
        print(f"Coup aux {couleur_coup}\n")
        print("Entrez votre coup (ex: B3 D3)")
        print("Q pour quitter")
        saisie = input("> ")
        
        if saisie.upper() == "Q":
            break
        else :
            try:
                coup = saisie.split()
                case_src = recherche_nom(coup[0])
                case_dst = recherche_nom(coup[1])
            except ValueError as err:
                print(err)
                continue

        # joue le coup
        piece = get_piece(plateau, case_src)
        if piece not in PIECES or get_couleur(piece) != to_move:
            print("Pièce adverse choisie, réessaie.\n")
            continue
        if not est_jouable(plateau, case_src, case_dst):
            print("Coup illégal, réessaie.\n")
            continue
        deplacement(plateau, case_src, case_dst)

        to_move = (to_move+1)%2


if __name__ == "__main__":
    play()
