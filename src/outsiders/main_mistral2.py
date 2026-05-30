import sys
import time
from typing import List, Tuple, Dict, Set

def main():
    # --- Lecture des données ---
    n_items = int(sys.stdin.readline().split()[1])
    S = int(sys.stdin.readline().split()[1])
    W = int(sys.stdin.readline().split()[1])

    items: Dict[int, Tuple[int, int, int]] = {}  # {id: (taille, poids, valeur)}
    for _ in range(n_items):
        iid, s, w, v = map(int, sys.stdin.readline().split())
        items[iid] = (s, w, v)

    # --- Pré-traitement ---
    sys.stdin.readline()  # "preprocessing 5000"

    # Calcul des scores de densité normalisée (GPT)
    densities = []
    for iid, (s, w, v) in items.items():
        density = v / ((s / S) + (w / W))
        densities.append((density, iid))
    densities.sort(reverse=True, key=lambda x: x[0])

    # Top 10% des objets (premium)
    premium_limit = max(1, n_items // 10)
    premium: Set[int] = {iid for _, iid in densities[:premium_limit]}

    # Variables de suivi
    available: Set[int] = set(items.keys())
    my_s, my_w = S, W
    opp_s, opp_w = S, W
    turn = 0

    # Poids pour le score hybride
    alpha, beta, gamma = 1.0, 0.5, 0.3

    # --- Boucle de jeu ---
    while True:
        # Lire l'objet pris par l'adversaire
        taken_line = sys.stdin.readline().strip()
        if not taken_line.startswith("taken"):
            break
        taken_id = int(taken_line.split()[1])

        if taken_id != -1 and taken_id in available:
            s, w, v = items[taken_id]
            opp_s -= s
            opp_w -= w
            available.remove(taken_id)

        # Lire le temps restant
        next_line = sys.stdin.readline().strip()
        if not next_line.startswith("next_item"):
            break

        # --- Choix de l'objet ---
        best_id = -1
        best_score = -1e30

        # Filtrer les objets valides
        candidates = []
        for iid in available:
            s, w, v = items[iid]
            if s <= my_s and w <= my_w:
                candidates.append(iid)

        # Si aucun objet valide, passer
        if not candidates:
            print(-1)
            sys.stdout.flush()
            continue

        # Évaluer chaque candidat
        for iid in candidates:
            s, w, v = items[iid]

            # Score dynamique (Claude)
            if my_s > 0 and my_w > 0:
                inv_my_s = 1.0 / my_s
                inv_my_w = 1.0 / my_w
                denom_my = s * inv_my_s + w * inv_my_w
                score_my = v / denom_my if denom_my > 0 else 0
            else:
                score_my = 0

            # Bonus premium (GPT)
            score_premium = v if iid in premium else 0

            # Pénalité si l'adversaire peut le prendre
            if opp_s > 0 and opp_w > 0:
                inv_opp_s = 1.0 / opp_s
                inv_opp_w = 1.0 / opp_w
                denom_opp = s * inv_opp_s + w * inv_opp_w
                score_opp = v / denom_opp if denom_opp > 0 else 0
            else:
                score_opp = 0

            # Score hybride
            score = alpha * score_my + beta * score_premium - gamma * score_opp

            if score > best_score:
                best_score = score
                best_id = iid

        # Simulation légère : vérifier l'impact sur le tour suivant
        if len(candidates) <= 3:  # Si peu de candidats, simuler
            best_sim_id = best_id
            best_sim_score = best_score

            for iid in candidates:
                # Simuler la prise de cet objet
                s, w, v = items[iid]
                new_my_s, new_my_w = my_s - s, my_w - w
                new_available = available - {iid}

                # Trouver le meilleur objet restant pour l'adversaire
                opp_best_score = -1
                for opp_iid in new_available:
                    opp_s_item, opp_w_item, opp_v = items[opp_iid]
                    if opp_s_item <= opp_s and opp_w_item <= opp_w:
                        opp_denom = opp_s_item / opp_s + opp_w_item / opp_w
                        opp_score = opp_v / opp_denom if opp_denom > 0 else 0
                        if opp_score > opp_best_score:
                            opp_best_score = opp_score

                # Score final = ma valeur - valeur max adverse
                sim_score = v - opp_best_score
                if sim_score > best_sim_score:
                    best_sim_score = sim_score
                    best_sim_id = iid

            best_id = best_sim_id

        # Mettre à jour les ressources
        if best_id != -1:
            s, w, v = items[best_id]
            my_s -= s
            my_w -= w
            available.remove(best_id)

        print(best_id)
        sys.stdout.flush()
        turn += 1

if __name__ == "__main__":
    main()