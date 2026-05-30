import sys

def readline():
    return sys.stdin.readline().strip()

# =====================================================
# Lecture instance
# =====================================================

n = int(readline().split()[1])
S = int(readline().split()[1])
W = int(readline().split()[1])

items = {}

for _ in range(n):
    iid, s, w, v = map(int, readline().split())

    items[iid] = (s, w, v)

readline()  # preprocessing 5000

# =====================================================
# Préprocessing
# =====================================================

available = set(items.keys())

my_s = S
my_w = W

opp_s = S
opp_w = W

done = False

# score global type Claude
densities = []

for iid, (s, w, v) in items.items():
    density = v / ((s / S) + (w / W))
    densities.append((density, iid))

densities.sort(reverse=True)

# top 10% des objets
premium = set()

limit = max(1, n // 10)

for _, iid in densities[:limit]:
    premium.add(iid)

# =====================================================
# Boucle
# =====================================================

while True:

    line = readline()

    if not line:
        break

    taken = int(line.split()[1])

    if taken >= 0 and taken in available:

        s, w, v = items[taken]

        opp_s -= s
        opp_w -= w

        available.remove(taken)

    line = readline()

    if not line:
        break

    if done:
        print(-1)
        sys.stdout.flush()
        continue

    # ============================================
    # Choix
    # ============================================

    best_id = -1
    best_score = -1e30

    inv_s = 1.0 / my_s if my_s > 0 else 0.0
    inv_w = 1.0 / my_w if my_w > 0 else 0.0

    for iid in available:

        s, w, v = items[iid]

        if s > my_s or w > my_w:
            continue

        # ------------------------
        # score Claude
        # ------------------------

        score = v / (s * inv_s + w * inv_w)

        # ------------------------
        # bonus objet convoité
        # ------------------------

        if iid in premium:
            score += v * 0.15

        # ------------------------
        # pénalité déséquilibre
        # ------------------------

        rem_s = my_s - s
        rem_w = my_w - w

        balance = abs(rem_s / S - rem_w / W)

        score -= balance * 10.0

        # ------------------------

        if score > best_score:
            best_score = score
            best_id = iid

    # ============================================
    # Aucun coup possible
    # ============================================

    if best_id == -1:

        done = True

        print(-1)
        sys.stdout.flush()

        continue

    # ============================================
    # Jouer
    # ============================================

    s, w, v = items[best_id]

    my_s -= s
    my_w -= w

    available.remove(best_id)

    print(best_id)
    sys.stdout.flush()