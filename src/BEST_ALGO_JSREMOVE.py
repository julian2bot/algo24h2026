import sys
import time


ALPHA = 1.0  # Poids de la valeur perso de l'obj (best à 1.0)
BETA = 0.5   # Poids des meilleurs objs (best à 0.5)
GAMMA = 0.3  # Poids des objs bien pour l'adverse (best à 0.3)

def lire_entree():
    n = int(sys.stdin.readline().split()[1])
    S = int(sys.stdin.readline().split()[1])
    W = int(sys.stdin.readline().split()[1])

    objs = {}
    for _ in range(n):
        id, taille, poids, valeur = map(int, sys.stdin.readline().split())
        objs[id] = (taille, poids, valeur)

    return n, S, W, objs

def calculer_densites(objs, S, W):
    pd = []
    for id, (taille, poids, valeur) in objs.items():
        densite = valeur / ((taille / S) + (poids / W))
        pd.append((densite, id))
    pd.sort(reverse=True, key=lambda x: x[0])
    return pd

def check_premium(densites, n):
    # les 20% meilleurs objes
    
    limite_premium = max(1, n // 10)
    return {id for _, id in densites[:limite_premium]}

def calculer_score_hybride(
    id_obj,
    taille,
    poids,
    valeur,
    ma_taille_restante,
    mon_poids_restant,
    taille_adversaire_restante,
    poids_adversaire_restant,
    est_premium,
):
    if ma_taille_restante > 0 and mon_poids_restant > 0:
        inv_ma_taille = 1.0 / ma_taille_restante
        inv_mon_poids = 1.0 / mon_poids_restant
        denom_moi = taille * inv_ma_taille + poids * inv_mon_poids
        score_dynamique = valeur / denom_moi if denom_moi > 0 else 0
    else:
        score_dynamique = 0

    score_premium = valeur if est_premium else 0

    if taille_adversaire_restante > 0 and poids_adversaire_restant > 0:
        inv_taille_adversaire = 1.0 / taille_adversaire_restante
        inv_poids_adversaire = 1.0 / poids_adversaire_restant
        denom_adversaire = taille * inv_taille_adversaire + poids * inv_poids_adversaire
        score_adversaire = valeur / denom_adversaire if denom_adversaire > 0 else 0
    else:
        score_adversaire = 0

    return ALPHA * score_dynamique + BETA * score_premium - GAMMA * score_adversaire

def simuler_tour_suivant(
    id_obj,
    objs_dispos,
    objs,
    taille_adversaire_restante,
    poids_adversaire_restant,
):
    
    nv_objs_dispos = objs_dispos - {id_obj}
    meilleur_score_adversaire = 0.0

    for id in nv_objs_dispos:
        taille, poids, valeur = objs[id]
        if taille <= taille_adversaire_restante and poids <= poids_adversaire_restant:
            # Calculer le score de l'adversaire pour cet obj
            denom = taille / taille_adversaire_restante + poids / poids_adversaire_restant
            score = valeur / denom if denom > 0 else 0
            if score > meilleur_score_adversaire:
                meilleur_score_adversaire = score

    return meilleur_score_adversaire

def choisir_meilleur_obj(
    objs_dispos,
    objs,
    ma_taille_restante,
    mon_poids_restant,
    taille_adversaire_restante,
    poids_adversaire_restant,
    objs_premium,
):
    
    # filtrer les objs impossibles
    candidats = []
    for id in objs_dispos:
        taille, poids, _ = objs[id]
        if taille <= ma_taille_restante and poids <= mon_poids_restant:
            candidats.append(id)

    if not candidats:
        return -1  # Aucun bon obj
    

    meilleur_id = -1
    meilleur_score = -1e30

    for id in candidats:
        taille, poids, valeur = objs[id]
        est_premium = id in objs_premium
        score = calculer_score_hybride(
            id, taille, poids, valeur,
            ma_taille_restante, mon_poids_restant,
            taille_adversaire_restante, poids_adversaire_restant,
            est_premium,
        )
        if score > meilleur_score:
            meilleur_score = score
            meilleur_id = id

    # 3 best objs
    if len(candidats) <= 3:
        meilleur_id_sim = meilleur_id
        meilleur_score_sim = meilleur_score

        for id in candidats:
            taille, poids, valeur = objs[id]
            # Score si je prends cet obj : ma valeur - meilleur score adverse
            score_sim = valeur - simuler_tour_suivant(
                id, objs_dispos, objs,
                taille_adversaire_restante, poids_adversaire_restant
            )
            if score_sim > meilleur_score_sim:
                meilleur_score_sim = score_sim
                meilleur_id_sim = id

        meilleur_id = meilleur_id_sim

    return meilleur_id




def main():
    n, S, W, objs = lire_entree()

    sys.stdin.readline()  # Lire "preprocessing 5000"

    # check les meilleurs objs
    densites = calculer_densites(objs, S, W)
    objs_premium = check_premium(densites, n)

    objs_dispos = set(objs.keys())
    ma_taille_restante = S
    mon_poids_restant = W
    taille_adversaire_restante = S
    poids_adversaire_restant = W




    while True:
        # check l'obj de l'adversaire
        ligne_pris = sys.stdin.readline().strip()
        if not ligne_pris.startswith("taken"):
            break

        id_pris_par_adversaire = int(ligne_pris.split()[1])
        if id_pris_par_adversaire != -1 and id_pris_par_adversaire in objs_dispos:
            taille, poids, _ = objs[id_pris_par_adversaire]
            taille_adversaire_restante -= taille
            poids_adversaire_restant -= poids
            objs_dispos.remove(id_pris_par_adversaire)

        ligne_temps = sys.stdin.readline().strip()
        if not ligne_temps.startswith("next_item"):
            break

        # choix obj
        id_choisi = choisir_meilleur_obj(
            objs_dispos, objs,
            ma_taille_restante, mon_poids_restant,
            taille_adversaire_restante, poids_adversaire_restant,
            objs_premium,
        )

        #  Update après obj
        if id_choisi != -1:
            taille, poids, _ = objs[id_choisi]
            ma_taille_restante -= taille
            mon_poids_restant -= poids
            objs_dispos.remove(id_choisi)

        print(id_choisi)
        sys.stdout.flush()

if __name__ == "__main__":
    main()