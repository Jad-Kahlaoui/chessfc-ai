from ia import joueur_alphabeta as nouvelle_ia
from ia import jouer_partie
from ia_old import joueur_alphabeta as ancienne_ia


NB_MATCHS = 25

score_new = 0
score_old = 0
nuls = 0

for i in range(NB_MATCHS):
    if i % 2 == 0:
        # nouvelle IA en blanc
        resultat = jouer_partie(nouvelle_ia(4), ancienne_ia(3))
        if resultat == 1:
            score_new += 1
        elif resultat == -1:
            score_old += 1
        else:
            nuls += 1
    else:
        # ancienne IA en blanc
        resultat = jouer_partie(ancienne_ia(3), nouvelle_ia(4))
        if resultat == 1:
            score_old += 1
        elif resultat == -1:
            score_new += 1
        else:
            nuls += 1

print("Nouvelle IA :", score_new)
print("Ancienne IA :", score_old)
print("Nuls        :", nuls)