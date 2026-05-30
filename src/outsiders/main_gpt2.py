import sys

def readline():
    return sys.stdin.readline().strip()

# ==========================================================
# Lecture
# ==========================================================

n = int(readline().split()[1])
S = int(readline().split()[1])
W = int(readline().split()[1])

items = {}

for _ in range(n):
    iid, s, w, v = map(int, readline().split())
    items[iid] = (s, w, v)

readline()  # preprocessing 5000

# ==========================================================
# Etat
# ==========================================================

available = set(items.keys())

my_s = S
my_w = W

opp_s = S
opp_w = W

done = False

# ==========================================================
# Outils
# ==========================================================

def density(iid, cap_s, cap_w):
    s, w, v = items[iid]

    if s > cap_s or w > cap_w:
        return -1

    return v / (s / cap_s + w / cap_w)

def build_plan(cap_s, cap_w, avail):

    ranked = []

    for iid in avail:
        ranked.append(
            (density(iid, cap_s, cap_w), iid)
        )

    ranked.sort(reverse=True)

    rem_s = cap_s
    rem_w = cap_w

    plan = []
    total = 0

    for _, iid in ranked:

        s, w, v = items[iid]

        if s <= rem_s and w <= rem_w:
            plan.append(iid)

            rem_s -= s
            rem_w -= w

            total += v

    return plan, total

# ==========================================================
# Construction du plan initial
# ==========================================================

plan, base_value = build_plan(S, W, available)

# ==========================================================
# Importance des objets du plan
# ==========================================================

criticality = {}

plan_set = set(plan)

for iid in plan:

    tmp_avail = available.copy()
    tmp_avail.remove(iid)

    _, value_without = build_plan(S, W, tmp_avail)

    criticality[iid] = base_value - value_without

# ==========================================================
# Ordre des objets critiques
# ==========================================================

critical_order = sorted(
    plan,
    key=lambda x: criticality[x],
    reverse=True
)

# ==========================================================
# Jeu
# ==========================================================

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

    choice = -1

    # ======================================================
    # 1. Objet critique encore disponible
    # ======================================================

    for iid in critical_order:

        if iid not in available:
            continue

        s, w, v = items[iid]

        if s <= my_s and w <= my_w:
            choice = iid
            break

    # ======================================================
    # 2. Suivre le plan
    # ======================================================

    if choice == -1:

        for iid in plan:

            if iid not in available:
                continue

            s, w, v = items[iid]

            if s <= my_s and w <= my_w:
                choice = iid
                break

    # ======================================================
    # 3. Rebuild si nécessaire
    # ======================================================

    if choice == -1:

        plan, _ = build_plan(
            my_s,
            my_w,
            available
        )

        for iid in plan:

            s, w, v = items[iid]

            if s <= my_s and w <= my_w:
                choice = iid
                break

    # ======================================================
    # 4. Aucun coup
    # ======================================================

    if choice == -1:

        done = True

        print(-1)
        sys.stdout.flush()

        continue

    # ======================================================
    # Jouer
    # ======================================================

    s, w, v = items[choice]

    my_s -= s
    my_w -= w

    available.remove(choice)

    print(choice)
    sys.stdout.flush()