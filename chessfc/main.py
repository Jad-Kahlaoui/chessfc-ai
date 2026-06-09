from constantes import *
from plateau import plateau_init, get_piece, get_couleur, recherche_nom
from regles import passe_jouable, est_jouable, jouer
from affichage import afficher


# Boucle de jeu
def play() -> None:
    plateau = plateau_init()
    balle = INIT_BALLE
    en_passant: Case | None = None
    to_move = BLANC

    while True:

        # détermine à qui de jouer
        if to_move == 0:
            couleur_coup = "Blancs"
        else :
            couleur_coup = "Noirs"

        # affichage du plateau
        afficher(plateau, balle)

        # saisie utilisateur
        print(f"Coup aux {couleur_coup}\n")
        print("- Entrez votre coup (ex: B3 D3)")
        print("- Q pour quitter")
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


        piece = get_piece(plateau, case_src)

        # vérification du coup
        if piece not in PIECES or get_couleur(piece) != to_move:
            print("Pièce adverse choisie, réessaie.\n")
            continue
        if case_src == balle:
            # frappe du balon
            legal = passe_jouable(plateau, balle, case_dst)
        else:
            # déplacement de la pièce
            legal = est_jouable(plateau, case_src, case_dst,en_passant)
        if not legal:
            print("Coup illégal, réessaie.\n")
            continue

        # joue le coup
        balle,en_passant = jouer(plateau, balle, case_src, case_dst,en_passant)

        to_move = (to_move+1)%2

    return None


if __name__ == "__main__":
    play()
