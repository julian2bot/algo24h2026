import sys
import time
from typing import Dict, Tuple, Set, List

def knapsack_dp(items_list, cap_s, cap_w, time_limit_s, start_time):
    """
    DP knapsack 2D bornée dans le temps.
    Retourne un dict {iid: marginal_value} = gain apporté par cet objet dans la solution optimale.
    On discrétise sur une grille réduite si les capacités sont grandes.
    """
    # Réduction de la grille si trop grande
    MAX_GRID = 150  # 150x150 = 22500 cellules, très rapide
    step_s = max(1, cap_s // MAX_GRID)
    step_w = max(1, cap_w // MAX_GRID)
    gs = cap_s // step_s
    gw = cap_w // step_w

    # dp[i][j] = meilleure valeur avec capacité taille i*step_s, poids j*step_w
    INF = float('inf')
    dp = [[0] * (gw + 1) for _ in range(gs + 1)]

    for iid, (s, w, v) in items_list:
        if time.time() - start_time > time_limit_s:
            break
        si = (s + step_s - 1) // step_s  # arrondi supérieur
        wi = (w + step_w - 1) // step_w
        if si > gs or wi > gw:
            continue
        # Parcours inverse pour knapsack 0/1
        for i in range(gs, si - 1, -1):
            for j in range(gw, wi - 1, -1):
                val = dp[i - si][j - wi] + v
                if val > dp[i][j]:
                    dp[i][j] = val

    return dp, step_s, step_w, gs, gw


def dp_value(dp, step_s, step_w, gs, gw, cap_s, cap_w):
    """Lit la valeur DP pour des capacités données."""
    i = min(cap_s // step_s, gs)
    j = min(cap_w // step_w, gw)
    return dp[i][j]


def compute_regret_scores(items: Dict[int, Tuple[int,int,int]],
                          available: Set[int],
                          my_s: int, my_w: int,
                          opp_s: int, opp_w: int,
                          dp, step_s, step_w, gs, gw) -> Dict[int, float]:
    """
    Pour chaque objet disponible, calcule un score composite :
      - gain_me   : combien cet objet améliore MON knapsack
      - regret    : combien je perds si l'adversaire le prend (il peut le prendre ?)
      - density   : valeur / ressources normalisées consommées
    """
    scores = {}
    base_me = dp_value(dp, step_s, step_w, gs, gw, my_s, my_w)

    for iid in available:
        s, w, v = items[iid]

        # Densité normalisée (robuste même quand capacité proche de 0)
        denom_me = (s / max(my_s, 1)) + (w / max(my_w, 1))
        density_me = v / denom_me if denom_me > 0 else 0

        # Gain marginal dans le knapsack (si on le prend)
        if s <= my_s and w <= my_w:
            gain_me = dp_value(dp, step_s, step_w, gs, gw, my_s - s, my_w - w) + v - base_me
            gain_me = max(gain_me, 0)
            fit_me = True
        else:
            gain_me = 0
            fit_me = False

        # Regret si l'adversaire prend cet objet (et peut le prendre)
        if s <= opp_s and w <= opp_w:
            denom_opp = (s / max(opp_s, 1)) + (w / max(opp_w, 1))
            threat = v / denom_opp if denom_opp > 0 else 0
        else:
            threat = 0

        scores[iid] = {
            'density': density_me,
            'gain': gain_me,
            'threat': threat,
            'fit': fit_me,
            'v': v, 's': s, 'w': w
        }

    return scores


def pick_best(scores: Dict, my_s: int, my_w: int,
              alpha=1.0, beta=0.8, gamma=0.6) -> int:
    """
    Score hybride adaptatif :
      alpha * density_normalisée + beta * gain_marginal_normalisé + gamma * threat_normalisée

    On normalise chaque composante par son max pour éviter les effets d'échelle.
    """
    candidates = {iid: d for iid, d in scores.items() if d['fit']}
    if not candidates:
        return -1

    max_density = max(d['density'] for d in candidates.values()) or 1
    max_gain    = max(d['gain']    for d in candidates.values()) or 1
    max_threat  = max(d['threat']  for d in candidates.values()) or 1

    best_id = -1
    best_score = -1e30

    for iid, d in candidates.items():
        score = (alpha * d['density'] / max_density
               + beta  * d['gain']    / max_gain
               + gamma * d['threat']  / max_threat)
        if score > best_score:
            best_score = score
            best_id = iid

    return best_id


def beam_search_pick(scores: Dict, items: Dict, available: Set[int],
                     my_s: int, my_w: int, opp_s: int, opp_w: int,
                     dp, step_s, step_w, gs, gw,
                     beam_k: int = 8, depth: int = 2) -> int:
    """
    Beam search sur `depth` coups pour les `beam_k` meilleurs candidats.
    Simule : je prends X → adversaire prend son meilleur → je prends mon meilleur.
    Retourne l'id du premier coup optimal.
    """
    candidates = [iid for iid, d in scores.items() if d['fit']]
    if not candidates:
        return -1

    # Trier par score hybride pour ne garder que le top beam_k
    max_density = max(scores[i]['density'] for i in candidates) or 1
    max_gain    = max(scores[i]['gain']    for i in candidates) or 1
    max_threat  = max(scores[i]['threat']  for i in candidates) or 1

    def quick_score(iid):
        d = scores[iid]
        return (d['density']/max_density + 0.8*d['gain']/max_gain + 0.6*d['threat']/max_threat)

    candidates.sort(key=quick_score, reverse=True)
    top = candidates[:beam_k]

    best_first = top[0]
    best_total = -1e30

    for first_id in top:
        s1, w1, v1 = items[first_id]
        avail2 = available - {first_id}
        ms2, mw2 = my_s - s1, my_w - w1

        # Adversaire prend son meilleur objet
        opp_best_v = 0
        opp_takes = -1
        for oiid in avail2:
            os2, ow2, ov2 = items[oiid]
            if os2 <= opp_s and ow2 <= opp_w:
                d2 = (os2/max(opp_s,1)) + (ow2/max(opp_w,1))
                sc = ov2/d2 if d2 > 0 else 0
                if sc > opp_best_v:
                    opp_best_v = sc
                    opp_takes = oiid

        avail3 = avail2 - {opp_takes} if opp_takes != -1 else avail2
        os3 = opp_s - items[opp_takes][0] if opp_takes != -1 else opp_s
        ow3 = opp_w - items[opp_takes][1] if opp_takes != -1 else opp_w

        # Mon meilleur deuxième coup
        my_best2 = 0
        for niid in avail3:
            ns, nw, nv = items[niid]
            if ns <= ms2 and nw <= mw2:
                nd = (ns/max(ms2,1)) + (nw/max(mw2,1))
                sc2 = nv/nd if nd > 0 else 0
                if sc2 > my_best2:
                    my_best2 = sc2

        # Score total = valeur immédiate + densité future estimée
        total = v1 + my_best2 - opp_best_v * 0.5
        if total > best_total:
            best_total = total
            best_first = first_id

    return best_first


def main():
    start = time.time()

    # --- Lecture des données ---
    n_items = int(sys.stdin.readline().split()[1])
    S = int(sys.stdin.readline().split()[1])
    W = int(sys.stdin.readline().split()[1])

    items: Dict[int, Tuple[int, int, int]] = {}
    for _ in range(n_items):
        iid, s, w, v = map(int, sys.stdin.readline().split())
        items[iid] = (s, w, v)

    # --- Preprocessing (5000 ms) ---
    sys.stdin.readline()  # "preprocessing 5000"

    # Trier les objets par densité décroissante pour le DP (greedy order = meilleur pour DP)
    items_sorted = sorted(items.items(), key=lambda x: x[1][2] / ((x[1][0]/S) + (x[1][1]/W)), reverse=True)

    # DP knapsack — on utilise 4 secondes max sur les 5 disponibles
    dp, step_s, step_w, gs, gw = knapsack_dp(items_sorted, S, W, 4.0, start)

    print(f"[Claude] DP ready in {time.time()-start:.2f}s, grid={gs}x{gw}, steps={step_s},{step_w}", file=sys.stderr)

    # --- Variables de jeu ---
    available: Set[int] = set(items.keys())
    my_s, my_w = S, W
    opp_s, opp_w = S, W
    turn = 0
    opp_history: List[Tuple[int,int,int]] = []  # (s, w, v) prises par l'adversaire

    # Paramètres adaptatifs
    alpha, beta, gamma = 1.0, 0.8, 0.6

    # --- Boucle de jeu ---
    while True:
        t0 = time.time()

        taken_line = sys.stdin.readline().strip()
        if not taken_line.startswith("taken"):
            break
        taken_id = int(taken_line.split()[1])

        if taken_id != -1 and taken_id in available:
            s, w, v = items[taken_id]
            opp_s -= s
            opp_w -= w
            opp_history.append((s, w, v))
            available.remove(taken_id)

        next_line = sys.stdin.readline().strip()
        if not next_line.startswith("next_item"):
            break

        # Recompute DP léger si les capacités ont beaucoup changé (facultatif)
        # Pour l'instant on utilise le DP initial et on ajuste par scoring

        # Calculer les scores
        scores = compute_regret_scores(
            items, available, my_s, my_w, opp_s, opp_w,
            dp, step_s, step_w, gs, gw
        )

        candidates_fit = [iid for iid, d in scores.items() if d['fit']]

        if not candidates_fit:
            print(-1)
            sys.stdout.flush()
            turn += 1
            continue

        # Choisir la stratégie selon le nombre de candidats et le temps restant
        elapsed = time.time() - t0
        time_budget = 0.45  # 450ms sur 500ms

        if len(candidates_fit) <= 20 or elapsed < time_budget - 0.05:
            # Beam search si assez de temps
            best_id = beam_search_pick(
                scores, items, available,
                my_s, my_w, opp_s, opp_w,
                dp, step_s, step_w, gs, gw,
                beam_k=min(12, len(candidates_fit)),
                depth=2
            )
        else:
            best_id = pick_best(scores, my_s, my_w, alpha, beta, gamma)

        if best_id == -1:
            best_id = pick_best(scores, my_s, my_w, alpha, beta, gamma)

        # Mettre à jour les ressources
        if best_id != -1:
            s, w, v = items[best_id]
            my_s -= s
            my_w -= w
            available.remove(best_id)
            print(f"[Claude] turn={turn} pick={best_id} v={v} s={s} w={w} | cap: S={my_s} W={my_w} | t={time.time()-t0:.3f}s", file=sys.stderr)

        print(best_id)
        sys.stdout.flush()
        turn += 1


if __name__ == "__main__":
    main()