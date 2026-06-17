## couche de traduction entre bibliothèque chessfc et notre moteur

from constantes import *
from chessfc.game import Piece, PlayerRole, Coord, Action, State
from plateau import plateau_vide, colonnes_jouables

## associatiation 1-to-1 entre nos pièces et ceux de chessfc
CORRESPONDANCES = {
    (Piece.PAWN, PlayerRole.WHITE): BPION,
    (Piece.KNIGHT, PlayerRole.WHITE): BCAVA,
    (Piece.BISHOP, PlayerRole.WHITE): BFOU,
    (Piece.ROOK, PlayerRole.WHITE): BTOUR,
    (Piece.QUEEN, PlayerRole.WHITE): BDAME,
    (Piece.PAWN, PlayerRole.BLACK): NPION,
    (Piece.KNIGHT, PlayerRole.BLACK): NCAVA,
    (Piece.BISHOP, PlayerRole.BLACK): NFOU,
    (Piece.ROOK, PlayerRole.BLACK): NTOUR,
    (Piece.QUEEN, PlayerRole.BLACK): NDAME,
}


def etat_vers_plateau(state: State) -> tuple[Plateau, Case]:
    """
        - Convertit un State en (plateau, balle)
        - Les coins hors-croix du State sont ignorés (MUR dans notre code)
        - Balle est suivie séparement 
    """
    plateau = plateau_vide()
    balle: Case = INIT_BALLE 

    for l in range(NB_LIGNES):
        deb, fin = colonnes_jouables(l)
        for c in range(deb, fin):
            piece, role, a_balle = state.board.board[l][c]  ## state.board.board
            code = CORRESPONDANCES.get((piece, role), VIDE)
            plateau[l][c] = code
            if a_balle:
                balle = (l, c)
                if code == VIDE:
                    plateau[l][c] = BALLE  ## ballon seul sur la case

    return plateau, balle


def role_vers_couleur(role: PlayerRole) -> int:
    ## PlayerRole de chessfc <-> couleur du moteur (BLANC/NOIR)
    return BLANC if role == PlayerRole.WHITE else NOIR


def coup_vers_action(case_src: Case, case_dst: Case) -> Action:
    ## conversion (ligne, colonne) qui commence à 0 contre 1 pour une Action
    ## changement x,y car dans chessfc x = colonne, y = ligne
    (ls, cs), (ld, cd) = case_src, case_dst
    return Action(Coord(x=cs + 1, y=ls + 1), Coord(x=cd + 1, y=ld + 1))
