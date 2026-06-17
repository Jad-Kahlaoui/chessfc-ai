"""Partie locale en console (humain et/ou IA)."""

from constantes import *
from plateau import plateau_init, get_piece, get_couleur, recherche_nom, get_nom
from regles import passe_jouable, est_jouable, jouer, final, get_etat
from affichage import afficher
from ia import joueur_alphabeta


# coup d'un humain : saisie clavier "B3 D3" etc...
def coup_humain(etat: list) -> tuple[Case, Case] | None:
    plateau, balle, joueur, en_passant = etat
    while True:
        print("- Entrez votre coup (ex: B3 D3)")
        print("- Q pour quitter")
        saisie = input("> ")

        if saisie.upper() == "Q":
            return None

        try:
            coup = saisie.split()
            case_src = recherche_nom(coup[0])
            case_dst = recherche_nom(coup[1])
        except (ValueError, IndexError) as err:
            print(err if isinstance(err, ValueError) else "Saisie invalide.")
            continue

        piece = get_piece(plateau, case_src)

        # vérification du coup
        if piece not in PIECES or get_couleur(piece) != joueur:
            print("Pièce adverse choisie, réessaie.\n")
            continue
        if case_src == balle:
            # frappe du ballon
            legal = passe_jouable(plateau, balle, case_dst)
        else:
            # déplacement de la pièce
            legal = est_jouable(plateau, case_src, case_dst, en_passant)  
        if not legal:
            print("Coup illégal, réessaie.\n")
            continue

        return (case_src, case_dst)


# Boucle de jeu, par défaut 2 humains
# TODO Changez avec serv du prof 
def play(strat_blanc=coup_humain, strat_noir=coup_humain, max_coups: int = 100) -> None:
    etat = get_etat(plateau_init(), INIT_BALLE, BLANC)

    for _ in range(max_coups):
        plateau, balle, to_move, en_passant = etat
        couleur_coup = "Blancs" if to_move == BLANC else "Noirs"

        # affichage du plateau
        afficher(plateau, balle)

        # test de fin de partie
        resultat = final(etat)
        if resultat is not None:
            if resultat == 1:
                print("But ! Les Blancs ont gagné.\n")
            elif resultat == -1:
                print("But ! Les Noirs ont gagné.\n")
            else:
                print("Match nul (pat).\n")
            return None

        # détermination du coup
        print(f"Coup aux {couleur_coup}\n")
        strat = strat_blanc if to_move == BLANC else strat_noir
        coup = strat(etat)

        if coup is None:  # interruption de partie par humain
            print("Partie interrompue.\n")
            return None

        case_src, case_dst = coup

        # si c'est une IA, on montre le coup choisi
        if strat is not coup_humain:
            print(f"L'IA joue {get_nom(case_src)} {get_nom(case_dst)}\n")

        balle, en_passant = jouer(plateau, balle, case_src, case_dst, en_passant)
        etat = get_etat(plateau, balle, (to_move + 1) % 2, en_passant)

    # nombre de coups maximum atteint
    print("Match nul (nombre de coups maximum atteint).\n")
    return None


if __name__ == "__main__":
    # petit menu de sélection des joueurs 
    ## TODO adapter avec serveur prof
    print("Chess FC")
    print("1) Humain vs Humain")
    print("2) Humain (Blancs) vs IA (Noirs)")
    print("3) IA (Blancs) vs Humain (Noirs)")
    print("4) IA vs IA")
    choix = input("> ").strip()

    if choix == "2":
        play(coup_humain, joueur_alphabeta(5))
    elif choix == "3":
        play(joueur_alphabeta(4), coup_humain)
    elif choix == "4":
        play(joueur_alphabeta(3), joueur_alphabeta(3))
    else:
        play(coup_humain, coup_humain)
