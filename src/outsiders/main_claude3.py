import sys
import time
from typing import Dict, Tuple, Set, List, Optional

# ─────────────────────────────────────────────
# DP Knapsack 2D rapide sur grille réduite
# ─────────────────────────────────────────────

def build_dp(items_list, cap_s, cap_w, time_limit_s, start_time,
             max_grid=120):
    """
    Construit le tableau DP 2D sur une grille réduite.
    Retourne (dp, step_s, step_w, gs, gw).
    """
    step_s = max(1, cap_s // max_grid)
    step_w = max(1, cap_w // max_grid)
    gs = cap_s // step_s
    gw = cap_w // step_w

    dp = [[0] * (gw + 1) for _ in range(gs + 1)]

    for iid, (s, w, v) in items_list:
        if time.time() - start_time > time_limit_s:
            break
        si = (s + step_s - 1) // step_s
        wi = (w + step_w - 1) // step_w
        if si > gs or wi > gw:
            continue
        for i in range(gs, si - 1, -1):
            row_i    = dp[i]
            row_prev = dp[i - si]
            for j in range(gw, wi - 1, -1):
                val = row_prev[j - wi] + v
                if val > row_i[j]:
                    row_i[j] = val

    return dp, step_s, step_w, gs, gw


def dp_val(dp, step_s, step_w, gs, gw, cap_s, cap_w):
    i = min(cap_s // step_s, gs)
    j = min(cap_w // step_w, gw)
    return dp[i][j]


def marginal_gain(dp, step_s, step_w, gs, gw,
                  cap_s, cap_w, s, w, v):
    """Gain marginal réel apporté par (s,w,v) dans l'état (cap_s, cap_w)."""
    if s > cap_s or w > cap_w:
        return -1e9
    base  = dp_val(dp, step_s, step_w, gs, gw, cap_s, cap_w)
    after = dp_val(dp, step_s, step_w, gs, gw, cap_s - s, cap_w - w) + v
    return after - base


# ─────────────────────────────────────────────
# Modèle adversaire : inférence de stratégie
# ─────────────────────────────────────────────

class OpponentModel:
    """
    Observe les choix adverses et estime sa stratégie :
      - 'density'  : il trie par v/((s/S)+(w/W))
      - 'value'    : il trie par v
      - 'random'   : on ne sait pas
    Prédit son prochain choix pour mieux l'anticiper.
    """
    def __init__(self, items, S, W):
        self.items = items
        self.S = S
        self.W = W
        self.history = []           # list of iid pris
        self.strategy = 'density'   # hypothèse initiale
        self.confidence = 0.5

    def update(self, taken_id, available_at_turn):
        if taken_id == -1:
            return
        self.history.append(taken_id)

        if len(self.history) < 3:
            return

        # Vérifier si ses choix correspondent à un tri par densité
        # On recompute le top-1 density et value à chaque tour
        density_matches = 0
        value_matches   = 0
        for i, iid in enumerate(self.history):
            avail = available_at_turn[i] if i < len(available_at_turn) else set()
            if not avail:
                continue
            # Top density
            best_d = max(avail, key=lambda x: self.items[x][2] / ((self.items[x][0]/self.S) + (self.items[x][1]/self.W)), default=None)
            # Top value
            best_v = max(avail, key=lambda x: self.items[x][2], default=None)
            if best_d == iid:
                density_matches += 1
            if best_v == iid:
                value_matches += 1

        n = len(self.history)
        if density_matches / n > 0.6:
            self.strategy = 'density'
            self.confidence = density_matches / n
        elif value_matches / n > 0.6:
            self.strategy = 'value'
            self.confidence = value_matches / n
        else:
            self.strategy = 'mixed'
            self.confidence = 0.3

    def predict_pick(self, available, opp_s, opp_w):
        """Retourne l'iid que l'adversaire va probablement prendre."""
        candidates = [iid for iid in available
                      if self.items[iid][0] <= opp_s and self.items[iid][1] <= opp_w]
        if not candidates:
            return -1

        if self.strategy == 'density':
            return max(candidates,
                       key=lambda x: self.items[x][2] / ((self.items[x][0]/max(opp_s,1)) + (self.items[x][1]/max(opp_w,1))))
        elif self.strategy == 'value':
            return max(candidates, key=lambda x: self.items[x][2])
        else:
            # Mixed : moyenne densité + valeur
            S, W = self.S, self.W
            return max(candidates,
                       key=lambda x: 0.5 * self.items[x][2] / ((self.items[x][0]/max(opp_s,1)) + (self.items[x][1]/max(opp_w,1)))
                                   + 0.5 * self.items[x][2])


# ─────────────────────────────────────────────
# Scoring principal
# ─────────────────────────────────────────────

def score_candidates(items, available, my_s, my_w, opp_s, opp_w,
                     dp, step_s, step_w, gs, gw,
                     opp_model: OpponentModel,
                     urgency_bonus: float = 2.0):
    """
    Score pour chaque objet candidat :
      - gain_me      : gain marginal DP (vision globale)
      - density_me   : densité normalisée (réactivité locale)
      - threat       : menace adversaire (densité depuis sa perspective)
      - urgency      : x urgency_bonus si l'adversaire va probablement le prendre MAINTENANT
    """
    opp_next = opp_model.predict_pick(available, opp_s, opp_w)

    scores = {}
    for iid in available:
        s, w, v = items[iid]
        fits = (s <= my_s and w <= my_w)

        # Gain marginal DP
        if fits:
            gm = marginal_gain(dp, step_s, step_w, gs, gw, my_s, my_w, s, w, v)
        else:
            gm = -1e9

        # Densité depuis ma perspective
        denom_me = (s / max(my_s, 1)) + (w / max(my_w, 1))
        dens_me = v / denom_me if denom_me > 0 else 0

        # Menace : densité depuis la perspective adverse
        denom_opp = (s / max(opp_s, 1)) + (w / max(opp_w, 1))
        threat = v / denom_opp if (denom_opp > 0 and s <= opp_s and w <= opp_w) else 0

        # Urgence : l'adversaire va-t-il le prendre maintenant ?
        is_urgent = (iid == opp_next)

        scores[iid] = {
            'fit': fits,
            'gm': gm,
            'dens': dens_me,
            'threat': threat,
            'urgent': is_urgent,
            'v': v, 's': s, 'w': w
        }

    return scores, opp_next


def pick_greedy(scores, urgency_bonus=2.0,
                w_gm=1.2, w_dens=0.8, w_threat=0.7):
    """Choix greedy normalisé sur les 3 composantes."""
    cands = {iid: d for iid, d in scores.items() if d['fit']}
    if not cands:
        return -1

    max_gm     = max(d['gm']     for d in cands.values()) or 1
    max_dens   = max(d['dens']   for d in cands.values()) or 1
    max_threat = max(d['threat'] for d in cands.values()) or 1

    best_id, best_sc = -1, -1e30
    for iid, d in cands.items():
        sc = (w_gm     * d['gm']     / max_gm
            + w_dens   * d['dens']   / max_dens
            + w_threat * d['threat'] / max_threat)
        if d['urgent']:
            sc *= urgency_bonus
        if sc > best_sc:
            best_sc, best_id = sc, iid

    return best_id


# ─────────────────────────────────────────────
# Beam search 2-ply avec modèle adversaire
# ─────────────────────────────────────────────

def beam_search(items, available, my_s, my_w, opp_s, opp_w,
                dp, step_s, step_w, gs, gw,
                opp_model: OpponentModel,
                beam_k=15, time_budget=0.35):
    """
    Pour les beam_k meilleurs premiers coups :
      1. Je prends X
      2. L'adversaire prédit prend son meilleur (selon son modèle inféré)
      3. J'estime ma valeur future = DP restant
    Retourne le meilleur premier coup.
    """
    t0 = time.time()

    scores, _ = score_candidates(items, available, my_s, my_w, opp_s, opp_w,
                                  dp, step_s, step_w, gs, gw, opp_model)
    cands = [iid for iid, d in scores.items() if d['fit']]
    if not cands:
        return -1

    # Trier et garder top beam_k
    max_gm   = max(scores[i]['gm']   for i in cands) or 1
    max_dens = max(scores[i]['dens'] for i in cands) or 1
    cands.sort(key=lambda x: scores[x]['gm']/max_gm + scores[x]['dens']/max_dens, reverse=True)
    top = cands[:beam_k]

    best_first, best_total = top[0], -1e30

    for first_id in top:
        if time.time() - t0 > time_budget:
            break

        s1, w1, v1 = items[first_id]
        ms2, mw2 = my_s - s1, my_w - w1
        avail2 = available - {first_id}

        # ── Coup adversaire prédit ──────────────────────
        opp_pick = opp_model.predict_pick(avail2, opp_s, opp_w)
        if opp_pick != -1:
            os2, ow2, _ = items[opp_pick]
            avail3 = avail2 - {opp_pick}
            opp_s2, opp_w2 = opp_s - os2, opp_w - ow2
        else:
            avail3 = avail2
            opp_s2, opp_w2 = opp_s, opp_w

        # ── Valeur future estimée via DP ─────────────────
        # Construire un DP léger sur avail3 (top items par densité)
        # Pour éviter de reconstruire un DP complet, on utilise le DP global
        # avec les capacités restantes comme proxy
        future_me = dp_val(dp, step_s, step_w, gs, gw, ms2, mw2)

        # Pénalité : valeur max que l'adversaire peut encore atteindre
        future_opp = dp_val(dp, step_s, step_w, gs, gw, opp_s2, opp_w2)

        # Score total : ma valeur immédiate + future - future adversaire pondérée
        total = v1 + future_me - 0.4 * future_opp

        if total > best_total:
            best_total, best_first = total, first_id

    return best_first


# ─────────────────────────────────────────────
# DP dynamique (recompilé sur objets restants)
# ─────────────────────────────────────────────

def rebuild_dp_dynamic(items, available, my_s, my_w, time_budget, max_grid=100):
    """
    Recompile un DP sur les objets ENCORE disponibles et mes capacités actuelles.
    Plus précis que le DP initial qui incluait des objets déjà pris.
    """
    t0 = time.time()
    # Trier par densité pour maximiser la qualité du DP tronqué
    avail_items = [(iid, items[iid]) for iid in available
                   if items[iid][0] <= my_s and items[iid][1] <= my_w]
    avail_items.sort(
        key=lambda x: x[1][2] / ((x[1][0]/max(my_s,1)) + (x[1][1]/max(my_w,1))),
        reverse=True
    )
    # Limiter à top 300 pour vitesse
    avail_items = avail_items[:300]

    return build_dp(avail_items, my_s, my_w, time_budget, t0, max_grid=max_grid)


# ─────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────

def main():
    start = time.time()

    n_items = int(sys.stdin.readline().split()[1])
    S = int(sys.stdin.readline().split()[1])
    W = int(sys.stdin.readline().split()[1])

    items: Dict[int, Tuple[int,int,int]] = {}
    for _ in range(n_items):
        iid, s, w, v = map(int, sys.stdin.readline().split())
        items[iid] = (s, w, v)

    sys.stdin.readline()  # "preprocessing 5000"

    # ── Preprocessing ────────────────────────────────────
    items_sorted = sorted(
        items.items(),
        key=lambda x: x[1][2] / ((x[1][0]/S) + (x[1][1]/W)),
        reverse=True
    )

    # DP global (3.5s max)
    dp, step_s, step_w, gs, gw = build_dp(items_sorted, S, W, 3.5, start, max_grid=120)
    print(f"[Claude v2] DP global ready {time.time()-start:.2f}s grid={gs}x{gw}", file=sys.stderr)

    # ── Variables de jeu ─────────────────────────────────
    available: Set[int] = set(items.keys())
    my_s, my_w = S, W
    opp_s, opp_w = S, W
    turn = 0

    opp_model = OpponentModel(items, S, W)
    opp_avail_history: List[Set[int]] = []   # état de available AVANT chaque coup adverse

    # DP courant (sera rafraîchi périodiquement)
    cur_dp, cur_step_s, cur_step_w, cur_gs, cur_gw = dp, step_s, step_w, gs, gw
    last_dp_rebuild = 0   # tour du dernier rebuild

    # ── Boucle de jeu ────────────────────────────────────
    while True:
        t0 = time.time()

        taken_line = sys.stdin.readline().strip()
        if not taken_line.startswith("taken"):
            break
        taken_id = int(taken_line.split()[1])

        # Enregistrer l'état AVANT que l'adversaire ait joué (pour inférence)
        opp_avail_history.append(set(available))

        if taken_id != -1 and taken_id in available:
            s, w, v = items[taken_id]
            opp_s -= s
            opp_w -= w
            available.remove(taken_id)

        opp_model.update(taken_id, opp_avail_history)

        next_line = sys.stdin.readline().strip()
        if not next_line.startswith("next_item"):
            break

        # ── Rebuild DP dynamique périodiquement ──────────
        # Tous les 10 tours ou si on a perdu >30% de nos capacités
        caps_lost = 1.0 - (my_s * my_w) / (S * W + 1e-9)
        should_rebuild = (
            (turn - last_dp_rebuild >= 10) or
            (turn == 5) or
            (caps_lost > 0.3 and turn - last_dp_rebuild >= 5)
        )

        time_for_dp = 0.12  # 120ms max pour rebuild
        time_remaining = 0.45 - (time.time() - t0)

        if should_rebuild and time_remaining > time_for_dp + 0.05:
            cur_dp, cur_step_s, cur_step_w, cur_gs, cur_gw = rebuild_dp_dynamic(
                items, available, my_s, my_w,
                time_budget=time_for_dp, max_grid=100
            )
            last_dp_rebuild = turn
            print(f"[Claude v2] DP rebuilt turn={turn} {time.time()-t0:.3f}s", file=sys.stderr)

        # ── Choix ─────────────────────────────────────────
        time_for_beam = 0.44 - (time.time() - t0)
        n_cands = sum(1 for iid in available if items[iid][0] <= my_s and items[iid][1] <= my_w)

        if n_cands == 0:
            print(-1)
            sys.stdout.flush()
            turn += 1
            continue

        # Beam search si on a du temps, sinon greedy
        if time_for_beam > 0.05 and n_cands > 0:
            beam_k = min(20, n_cands)
            best_id = beam_search(
                items, available, my_s, my_w, opp_s, opp_w,
                cur_dp, cur_step_s, cur_step_w, cur_gs, cur_gw,
                opp_model,
                beam_k=beam_k,
                time_budget=min(time_for_beam - 0.02, 0.30)
            )
        else:
            scores, _ = score_candidates(
                items, available, my_s, my_w, opp_s, opp_w,
                cur_dp, cur_step_s, cur_step_w, cur_gs, cur_gw,
                opp_model
            )
            best_id = pick_greedy(scores)

        if best_id == -1:
            scores, _ = score_candidates(
                items, available, my_s, my_w, opp_s, opp_w,
                cur_dp, cur_step_s, cur_step_w, cur_gs, cur_gw,
                opp_model
            )
            best_id = pick_greedy(scores)

        if best_id != -1:
            s, w, v = items[best_id]
            my_s -= s
            my_w -= w
            available.remove(best_id)
            strat = opp_model.strategy
            conf  = opp_model.confidence
            print(f"[Claude v2] t={turn} pick={best_id} v={v} | S={my_s} W={my_w} "
                  f"| opp={strat}({conf:.0%}) | {time.time()-t0:.3f}s", file=sys.stderr)

        print(best_id)
        sys.stdout.flush()
        turn += 1


if __name__ == "__main__":
    main()