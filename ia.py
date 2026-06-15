import random

from constantes import *
from plateau import get_piece, get_couleur, plateau_init
from regles import coups_legaux, jouer, final, get_etat
from affichage import afficher
from zobrist import zobrist_hash

# --------------------------------------------------------------------------
# Fonction d'évaluation
# --------------------------------------------------------------------------

def copier_plateau(plateau: Plateau) -> Plateau:
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
    # NB : appelée uniquement sur une position non terminale (final() déjà testé
    # par alphabeta), d'où l'absence de gestion de fin de partie ici.

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

# Table de transposition , sert à réexplorer même branche avec paramètres alpha/beta différents
EXACT = 0       # valeur exacte
BORNE_INF = 1   # valeur minorée (coupure beta)
BORNE_SUP = -1  # valeur majorée (coupure alpha)


def alphabeta(etat: list, prof: int, alpha: float, beta: float, table_transpo: dict, repetition_transpo: dict) -> float:
    # joueur = couleur au trait ; BLANC maximise, NOIR minimise.
    plateau, balle, joueur, en_passant = etat
    alpha_initial, beta_initial = alpha, beta
    h = zobrist_hash(etat)

    # répétition dans la ligne d'analyse (logique 2-fold)
    if repetition_transpo.get(h, 0) >= 2:
        return 0.0 # testé AVANT l'évaluation, on ne mémorise pas le noeud

    # consultation des positions déjà évaluées
    entree = table_transpo.get(h)
    if entree is not None and entree[0] >= prof:
        _, flag, valeur = entree
        if flag == EXACT:
            return valeur
        if flag == BORNE_INF:
            alpha = max(alpha, valeur) # minorant relève alpha
        elif flag == BORNE_SUP:
            beta = min(beta, valeur) # majorant abaisse beta
        if alpha >= beta:
            return valeur

    coups = coups_legaux(etat)

    # évaluation en fin d'exploration (but, pat ou répétition)
    fin = final(etat, repetition_transpo, coups)
    if fin is not None:
        return float(fin * (1000 + prof)) # on ajoute prof pour donner la priorité aux mats rapides

    if prof == 0:
        return evaluer(etat)

    # exploration des coup sinon
    adversaire = (joueur+1)%2

    if joueur == BLANC:
        valeur = float("-inf")
        for case_src, case_dst in coups:
            copie = copier_plateau(plateau)
            new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
            new_etat = get_etat(copie, new_balle, adversaire, new_ep)
            nh = zobrist_hash(new_etat)

            # make/unmake pour remonter l'historique de repetitions
            repetition_transpo[nh] = repetition_transpo.get(nh, 0) + 1   # make
            valeur = max(valeur, alphabeta(new_etat, prof - 1, alpha, beta, table_transpo, repetition_transpo))
            repetition_transpo[nh] -= 1 # unmake
            
            alpha = max(alpha, valeur)
            if alpha >= beta:
                break  # coupure beta
    else:
        valeur = float("inf")
        for case_src, case_dst in coups:
            copie = copier_plateau(plateau)
            new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
            new_etat = get_etat(copie, new_balle, adversaire, new_ep)
            nh = zobrist_hash(new_etat)

            # make/unmake pour remonter l'historique de repetitions
            repetition_transpo[nh] = repetition_transpo.get(nh, 0) + 1   # make
            valeur = min(valeur, alphabeta(new_etat, prof - 1, alpha, beta, table_transpo, repetition_transpo))
            repetition_transpo[nh] -= 1  # unmake
            
            beta = min(beta, valeur)
            if alpha >= beta:
                break  # coupure alpha

    # mémorisation de la position pour réexplorer si nécessaire
    if valeur <= alpha_initial:
        flag = BORNE_SUP
    elif valeur >= beta_initial:
        flag = BORNE_INF
    else:
        flag = EXACT

    # remplace l'entrée seulement si elle est au moins aussi profonde
    ancienne = table_transpo.get(h)
    if ancienne is None or prof >= ancienne[0]:
        table_transpo[h] = (prof, flag, valeur)

    return valeur


def meilleur_coup(etat: list, prof: int, historique: dict[int, int] | None = None, table_transpo: dict | None = None) -> tuple[Case, Case] | None:
    # choisit le coup qui maximise (Blancs) ou minimise (Noirs) la
    # valeur alpha-beta. En cas d'egalité, choix aléatoire
    plateau, balle, joueur, en_passant = etat
    coups = coups_legaux(etat)
    if not coups:
        return None

    adversaire = (joueur + 1) % 2
    meilleurs: list[tuple[Case, Case]] = []
    meilleure_valeur = float("-inf") if joueur == BLANC else float("inf")

    # on réutilise la table_transpo passé en argument (si présente)
    if table_transpo is None:
        table_transpo = {}
    if historique:  # historique non vide
        repetition_transpo = dict(historique) # copie de l'historique
    else:
        repetition_transpo = {zobrist_hash(etat): 1} #initialisation de l'historique

    for case_src, case_dst in coups:
        copie = copier_plateau(plateau)
        new_balle, new_ep = jouer(copie, balle, case_src, case_dst, en_passant)
        new_etat = get_etat(copie, new_balle, adversaire, new_ep)
        nh = zobrist_hash(new_etat)

        # make/unmake pour remonter l'historique de repetitions
        repetition_transpo[nh] = repetition_transpo.get(nh, 0) + 1   # make
        valeur = alphabeta(new_etat, prof - 1, float("-inf"), float("inf"), table_transpo, repetition_transpo)
        repetition_transpo[nh] -= 1 # unmake

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
    table_transpo: dict = {}  # conservée d'un coup à l'autre pour ce joueur
    def strat(etat: list) -> tuple[Case, Case] | None:
        return meilleur_coup(etat, prof, table_transpo=table_transpo)
    return strat


# --------------------------------------------------------------------------
# Moteur de partie automatique (IA vs IA, ou test)
# --------------------------------------------------------------------------

def jouer_partie(strat_blanc, strat_noir, debug: bool = False,
                 max_coups: int = 200) -> int | None:

    etat = get_etat(plateau_init(), INIT_BALLE, BLANC)
    repetition_transpo: dict[int, int] = {}  # comptage des positions (répétition)

    for _ in range(max_coups):
        plateau, balle, trait, en_passant = etat

        # comptage de la position courante puis test de fin de partie
        h = zobrist_hash(etat)
        repetition_transpo[h] = repetition_transpo.get(h, 0) + 1

        resultat = final(etat, repetition_transpo)
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
