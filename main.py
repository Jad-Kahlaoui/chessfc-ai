## point d'entrée pour jouer contre le serveur via encapsulation de l'IA
## dans les trois callbacks avant d'appeler start()

import sys

from chessfc.player import start
from chessfc.player_types import Environment, ClientOption, ServerOption
from chessfc.game import Action, Coord, Duration, PlayerRole, Score, State, MaybeMaybeAction

from constantes import *
from plateau import colonnes_jouables, get_nom
from affichage import afficher
from regles import jouer, get_etat
from ia import meilleur_coup, copier_plateau
from zobrist import zobrist_hash
from adaptateur import etat_vers_plateau, role_vers_couleur, coup_vers_action

## profondeur de recherche de l'alpha-beta - TODO à modifier
PROFONDEUR = 3


def detecter_en_passant(precedent: Plateau | None, courant: Plateau, couleur_adverse: int) -> Case | None:
    """Retrouve la cible de prise en passant en comparant le plateau prévu
    apres notre dernier coup avec le plateau recu du serveur car il 
    faut detecter soi-meme un double pas de pion adverse entre nos deux
    tours
    """
    if precedent is None:
        return None

    pion = NPION if couleur_adverse == NOIR else BPION
    sources = []
    arrivees = []
    for l in range(NB_LIGNES):
        deb, fin = colonnes_jouables(l)
        for c in range(deb, fin):
            if precedent[l][c] == pion and courant[l][c] != pion:
                sources.append((l, c))
            elif courant[l][c] == pion and precedent[l][c] != pion:
                arrivees.append((l, c))

    if len(sources) == 1 and len(arrivees) == 1:
        (ls, cs), (la, ca) = sources[0], arrivees[0]
        if ls == la and abs(ca - cs) == 2:
            return (ls, (cs + ca) // 2)
    return None


# ---------------------------------------------------------------------------
#         Callbacks
# ---------------------------------------------------------------------------

def start_fn(game_id: str, environment: Environment, role: PlayerRole,
             start_clock: Duration, play_clock: Duration, total_clock: Duration,
             limit_number_of_turn: int, state: State,
             actions: MaybeMaybeAction) -> Environment:
    print(f"Debut de partie {game_id} : nous jouons "
          f"{'les Blancs' if role == PlayerRole.WHITE else 'les Noirs'}")
    print(f"  temps par tour : {play_clock} ns (0 = illimite)")
    print(f"  temps total    : {total_clock} ns (0 = illimite)")
    print(f"  limite de tours: {limit_number_of_turn} (0 = aucune)")
    
    ## precedent: plateau du coup d'avant
    ## historique : comptage des positions réelles (répétitions)
    return {"precedent": None, "historique": {}}


def strategy_fn(game_id: str, environment: Environment, state: State,
                actions: MaybeMaybeAction, role: PlayerRole,
                player_clock: Duration) -> tuple[Action, Environment]:
    plateau, balle = etat_vers_plateau(state)
    afficher(plateau, balle)  
    couleur = role_vers_couleur(role)
    adverse = (couleur + 1) % 2

    en_passant = detecter_en_passant(environment.get("precedent"), plateau, adverse)

    etat = get_etat(plateau, balle, couleur, en_passant)

    ## on compte la position courante dans l'historique réel pour anticiper les répétitions
    historique = dict(environment.get("historique") or {})
    historique[zobrist_hash(etat)] = historique.get(zobrist_hash(etat), 0) + 1

    ## [CORRECTION] table de transposition recreee a CHAQUE tour. Ses valeurs
    ## dependent du contexte de repetition courant (alphabeta renvoie 0 sur une
    ## repetition) : les conserver d'un tour a l'autre empoisonnait la recherche
    ## et menait a des parties toujours nulles. La table sert toujours a
    ## l'interieur d'un meme coup, on ne la partage juste plus entre les coups.
    coup = meilleur_coup(etat, PROFONDEUR, historique, {})

    if coup is None:
        ## aucun coup legal: serveur doit normalement conclure la partie
        ## mais retourne un coup 'statique' en tant que fallback au cas où
        return Action(Coord(5, 4), Coord(5, 4)), environment

    case_src, case_dst = coup
    print(f"Nous jouons {get_nom(case_src)} {get_nom(case_dst)}")

    ## plateau pour le tour suivant
    prevision = copier_plateau(plateau)
    jouer(prevision, balle, case_src, case_dst, en_passant)
    environment = dict(environment)
    environment["precedent"] = prevision
    environment["historique"] = historique

    return coup_vers_action(case_src, case_dst), environment


def final_fn(game_id: str, environment: Environment, state: State,
             actions: MaybeMaybeAction, score: Score, role: PlayerRole,
             player_clock: Duration) -> None:
    couleur = role_vers_couleur(role)
    if score == 0:
        resultat = "match nul"
    elif (score > 0) == (couleur == BLANC):
        resultat = "VICTOIRE"
    else:
        resultat = "défaite"
    print(f"Fin de partie {game_id} : score {score} -> {resultat}")


def main() -> None:
    server = ServerOption()
    client = ClientOption(name="jad-test")
    if len(sys.argv) > 1:
        server.host = sys.argv[1]
    if len(sys.argv) > 2:
        server.port = sys.argv[2]
    if len(sys.argv) > 3:
        client.name = sys.argv[3]

    start(start_fn, strategy_fn, final_fn, client, server)


if __name__ == "__main__":
    main()
