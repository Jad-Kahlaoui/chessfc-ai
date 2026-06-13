import random

from constantes import *
from plateau import get_piece, get_couleur, plateau_init
from regles import coups_legaux, jouer, final, get_etat
from affichage import afficher

# --------------------------------------------------------------------------
# Fonction d'évaluation
# --------------------------------------------------------------------------

def copier_plateau(plateau: list[list[int]]) -> list[list[int]]:
    # copie profonde pour simuler
    # un coup sans abimer le vrai plateau 
    return [ligne[:] for ligne in plateau]

# valeur num de chaque pièce
VALEURS = {
    BPION: 1.0, NPION: 1.0,
    BCAVA: 3.0, NCAVA: 3.0,
    BFOU: 3.0, NFOU: 3.0,
    BTOUR: 5.0, NTOUR: 5.0,
    BDAME: 9.0, NDAME: 9.0,
}

## fonction de calcul de score pour chaque état de la partie
def evaluer(etat: list) -> float:
    plateau, balle, joueur, en_passant = etat
    # Les Blancs maximisent (ils poussent la balle vers la colonne 8), les Noirs
    # minimisent (ils poussent vers la colonne 0)

    # fin de jeu
    fin = final(etat)
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

def alphabeta(etat: list, prof: int, alpha: float, beta: float) -> float:
    # joueur = couleur au trait ; BLANC maximise, NOIR minimise.
    plateau, balle, joueur, en_passant = etat

    fin = final(etat)
    if fin is not None:
        return float(fin * 1000)

    if prof == 0:
        return evaluer(etat)

    coups = coups_legaux(etat)
    if not coups:
        return evaluer(etat)

    adversaire = (joueur + 1) % 2

    if joueur == BLANC:
        valeur = float("-inf")
        for case_src, case_dst in coups:
            copie = copier_plateau(plateau)
            new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
            new_etat = get_etat(copie, new_balle, adversaire, new_ep)
            valeur = max(valeur, alphabeta(new_etat, prof - 1, alpha, beta))
            alpha = max(alpha, valeur)
            if alpha >= beta:
                break  # coupure beta
        return valeur
    else:
        valeur = float("inf")
        for case_src, case_dst in coups:
            copie = copier_plateau(plateau)
            new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
            new_etat = get_etat(copie, new_balle, adversaire, new_ep)
            valeur = min(valeur, alphabeta(new_etat, prof - 1, alpha, beta))
            beta = min(beta, valeur)
            if alpha >= beta:
                break  # coupure alpha
        return valeur


def meilleur_coup(etat: list, prof: int) -> tuple[Case, Case] | None:
    # choisit le coup qui maximise (Blancs) ou minimise (Noirs) la
    # valeur alpha-beta. En cas d'egalité, choix aléatoire
    plateau, balle, joueur, en_passant = etat
    coups = coups_legaux(etat)
    if not coups:
        return None

    adversaire = (joueur + 1) % 2
    meilleurs: list[tuple[Case, Case]] = []
    meilleure_valeur = float("-inf") if joueur == BLANC else float("inf")

    for case_src, case_dst in coups:
        copie = copier_plateau(plateau)
        new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
        new_etat = get_etat(copie, new_balle, adversaire, new_ep)
        valeur = alphabeta(new_etat, prof - 1, float("-inf"), float("inf"))

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
    def strat(etat: list) -> tuple[Case, Case] | None:
        return meilleur_coup(etat, prof)
    return strat


# --------------------------------------------------------------------------
# Moteur de partie automatique (IA vs IA, ou test)
# --------------------------------------------------------------------------

def jouer_partie(strat_blanc, strat_noir, debug: bool = False,
                 max_coups: int = 200) -> int | None:

    etat = get_etat(plateau_init(), INIT_BALLE, BLANC)

    for _ in range(max_coups):
        plateau, balle, trait, en_passant = etat

        # fin de partie
        resultat = final(etat)
        if resultat is not None:
            if debug:
                afficher(plateau, balle)
                print(f"Resultat : {resultat}")
            return resultat

        strat = strat_blanc if trait == BLANC else strat_noir
        coup = strat(etat)
        if coup is None:
            return 0  # aucun coup

        case_src, case_dst = coup
        balle, en_passant = jouer(plateau, balle, case_src, case_dst, en_passant)

        if debug:
            afficher(plateau, balle)

        etat = get_etat(plateau, balle, (trait + 1) % 2, en_passant)

    return None

# --------------------------------------------------------------------------
# Stratégie 2 : TODO A faire  
# --------------------------------------------------------------------------
