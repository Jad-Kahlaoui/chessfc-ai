import random

from constantes import *
from plateau import get_piece, get_couleur, plateau_init
from regles import coups_legaux, jouer, final
from affichage import afficher


def copier_plateau(plateau: list[list[int]]) -> list[list[int]]:
    # copie profonde pour simuler
    # un coup sans abimer le vrai plateau 
    return [ligne[:] for ligne in plateau]

# --------------------------------------------------------------------------
# Fonction d'évaluation de la partie
# --------------------------------------------------------------------------

# valeur num de chaque pièce
VALEURS = {
    BPION: 1.0, NPION: 1.0,
    BCAVA: 3.0, NCAVA: 3.0,
    BFOU: 3.0, NFOU: 3.0,
    BTOUR: 5.0, NTOUR: 5.0,
    BDAME: 9.0, NDAME: 9.0,
}

## fonction de calcul de score pour chaque état de la partie
def evaluer(plateau: list[list[int]], balle: Case, joueur: int,
            en_passant: Case | None = None) -> float:
    # Les Blancs maximisent (ils poussent la balle vers la colonne 8), les Noirs
    # minimisent (ils poussent vers la colonne 0)

    # fin de jeu
    fin = final(plateau, balle, joueur, en_passant)
    if fin == 1:
        return 1000.0   # les Blancs ont marqué
    if fin == -1:
        return -1000.0  # les Noirs ont marqué
    if fin == 0:
        return 0.0  ## match nul

    score = 0.0

    # calcul de score
    for ligne in plateau:
        for piece in ligne:
            if piece in VALEURS:
                if get_couleur(piece) == BLANC:
                    score += VALEURS[piece]
                else:
                    score -= VALEURS[piece]

    # progression de la balle : plus la colonne est grande, mieux c'est pour
    # les Blancs (but noir colonne 8), et inversement 
    # Colonne centrale = 4 -> neutre
    score += (balle[1] - 4) * 0.5 # TODO Optimisation de la val 

    # controle de la balle : bonus pour celui dont une piece occupe la balle
    porteur = get_piece(plateau, balle)
    if porteur in PIECES:
        score += 0.3 if get_couleur(porteur) == BLANC else -0.3 #TODO Optimiser le bonus 

    return score

# --------------------------------------------------------------------------
# Stratégie 1 : minmax 
# --------------------------------------------------------------------------

def alphabeta(plateau: list[list[int]], balle: Case, joueur: int,
              prof: int, alpha: float, beta: float,
              en_passant: Case | None = None) -> float:
    # joueur = couleur au trait ; BLANC maximise, NOIR minimise.

    fin = final(plateau, balle, joueur, en_passant)
    if fin is not None:
        return float(fin * 1000)

    if prof == 0:
        return evaluer(plateau, balle, joueur, en_passant)

    coups = coups_legaux(plateau, balle, joueur, en_passant)
    if not coups:
        return evaluer(plateau, balle, joueur, en_passant)

    adversaire = (joueur + 1) % 2

    if joueur == BLANC:
        valeur = float("-inf")
        for case_src, case_dst in coups:
            copie = copier_plateau(plateau)
            new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
            valeur = max(valeur, alphabeta(copie, new_balle, adversaire,
                                           prof - 1, alpha, beta, new_ep))
            alpha = max(alpha, valeur)
            if alpha >= beta:
                break  # coupure beta
        return valeur
    else:
        valeur = float("inf")
        for case_src, case_dst in coups:
            copie = copier_plateau(plateau)
            new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
            valeur = min(valeur, alphabeta(copie, new_balle, adversaire,
                                           prof - 1, alpha, beta, new_ep))
            beta = min(beta, valeur)
            if alpha >= beta:
                break  # coupure alpha
        return valeur


def meilleur_coup(plateau: list[list[int]], balle: Case, joueur: int,
                  prof: int, en_passant: Case | None = None) -> tuple[Case, Case] | None:
    # choisit le coup qui maximise (Blancs) ou minimise (Noirs) la
    # valeur alpha-beta. En cas d'egalité, choix aléatoire
    coups = coups_legaux(plateau, balle, joueur, en_passant)
    if not coups:
        return None

    adversaire = (joueur + 1) % 2
    meilleurs: list[tuple[Case, Case]] = []
    meilleure_valeur = float("-inf") if joueur == BLANC else float("inf")

    for case_src, case_dst in coups:
        copie = copier_plateau(plateau)
        new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
        valeur = alphabeta(copie, new_balle, adversaire,
                           prof - 1, float("-inf"), float("inf"), new_ep)

        if joueur == BLANC:
            if valeur > meilleure_valeur:
                meilleure_valeur = valeur
                meilleurs = [(case_src, case_dst)]
            elif valeur == meilleure_valeur:
                meilleurs.append((case_src, case_dst))
        else:
            if valeur < meilleure_valeur:
                meilleure_valeur = valeur
                meilleurs = [(case_src, case_dst)]
            elif valeur == meilleure_valeur:
                meilleurs.append((case_src, case_dst))

    return random.choice(meilleurs)


def joueur_alphabeta(prof: int = 2):
    def strat(plateau: list[list[int]], balle: Case, joueur: int,
              en_passant: Case | None = None) -> tuple[Case, Case] | None:
        return meilleur_coup(plateau, balle, joueur, prof, en_passant)
    return strat


# --------------------------------------------------------------------------
# Moteur de partie automatique (IA vs IA, ou test)
# --------------------------------------------------------------------------

def jouer_partie(strat_blanc, strat_noir, debug: bool = False,
                 max_coups: int = 200) -> int | None:

    plateau = plateau_init()
    balle = INIT_BALLE
    en_passant: Case | None = None
    trait = BLANC

    for _ in range(max_coups):
        # fin de partie 
        resultat = final(plateau, balle, trait, en_passant)
        if resultat is not None:
            if debug:
                afficher(plateau, balle)
                print(f"Resultat : {resultat}")
            return resultat

        strat = strat_blanc if trait == BLANC else strat_noir
        coup = strat(plateau, balle, trait, en_passant)
        if coup is None:
            return 0  # aucun coup 

        case_src, case_dst = coup
        balle, en_passant = jouer(plateau, balle, case_src, case_dst, en_passant)

        if debug:
            afficher(plateau, balle)

        trait = (trait + 1) % 2

    return None 

# --------------------------------------------------------------------------
# Stratégie 2 : TODO A faire  
# --------------------------------------------------------------------------
