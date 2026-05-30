import random
import copy

# =========================
# PARAMS
# =========================

N = 10
POP_SIZE = 120
GENERATIONS = 2000
MUTATION_RATE = 0.4

EARLY_FAIL = 3  # stop rapide si pas de progression

# =========================
# UTIL
# =========================

def sign(a):
    return (a > 0) - (a < 0)

def in_bounds(x, y):
    return 0 <= x < N and 0 <= y < N

# =========================
# RAY CHECK
# =========================

def ray_visible(grid, x, y, light):
    dx = light.x - x
    dy = light.y - y

    if dx != 0 and dy != 0:
        return False

    dist = abs(dx + dy)
    if dist > light.r:
        return False

    sx = sign(dx)
    sy = sign(dy)

    cx, cy = x + sx, y + sy

    while (cx, cy) != (light.x, light.y):

        for b in grid["blocks"]:
            if b.x == cx and b.y == cy and b.s == 1:
                return False

        for l in grid["lights"]:
            if l.x == cx and l.y == cy:
                return False

        cx += sx
        cy += sy

    return True

def get_visible(grid, x, y):
    res = []
    for l in grid["lights"]:
        if ray_visible(grid, x, y, l):
            dx = l.x - x
            dy = l.y - y
            if dx != 0:
                res.append((-sign(dx), 0))
            else:
                res.append((0, -sign(dy)))
    return res

# =========================
# SIMULATION + PRUNING
# =========================

def simulate(grid):
    x, y = grid["hamster"]

    dx, dy = 0, 0

    steps = 0
    stuck_counter = 0

    visited = set()

    for _ in range(2000):

        state = (x, y, dx, dy)
        if state in visited:
            return 0
        visited.add(state)

        vis = get_visible(grid, x, y)

        if len(vis) >= 2:
            return steps

        if len(vis) == 1:
            dx, dy = vis[0]

        if dx == 0 and dy == 0:
            return steps

        nx, ny = x + dx, y + dy

        if not in_bounds(nx, ny):
            return steps

        blocked = False

        for b in grid["blocks"]:
            if b.x == nx and b.y == ny and b.s == 1:
                blocked = True

        for l in grid["lights"]:
            if l.x == nx and l.y == ny:
                blocked = True

        if blocked:
            return steps

        # SWITCH
        for s in grid["switches"]:
            if s.x == nx and s.y == ny:
                for b in grid["blocks"]:
                    if b.g == s.g:
                        b.s = 1 - b.s

        x, y = nx, ny
        steps += 1

        # 🔥 EARLY PRUNING INTELLIGENT
        if steps < 5:
            stuck_counter += 1
            if stuck_counter >= EARLY_FAIL:
                return steps  # abandon rapide

    return 0

# =========================
# GENERATION
# =========================

def random_grid():
    cells = [(x, y) for x in range(N) for y in range(N)]

    h = random.choice(cells)
    cells.remove(h)

    lights = []
    blocks = []
    switches = []

    for _ in range(random.randint(2, 5)):
        if not cells: break
        c = random.choice(cells)
        cells.remove(c)
        lights.append(type("L", (), {"x": c[0], "y": c[1], "r": random.randint(1, N)}))

    for _ in range(random.randint(3, 8)):
        if not cells: break
        c = random.choice(cells)
        cells.remove(c)
        blocks.append(type("B", (), {"x": c[0], "y": c[1], "g": random.randint(0,5), "s": random.randint(0,1)}))

    for _ in range(random.randint(1, 3)):
        if not cells: break
        c = random.choice(cells)
        cells.remove(c)
        switches.append(type("S", (), {"x": c[0], "y": c[1], "g": random.randint(0,5)}))

    return {
        "hamster": h,
        "lights": lights,
        "blocks": blocks,
        "switches": switches
    }

# =========================
# MUTATION
# =========================

def mutate(g):
    g = copy.deepcopy(g)

    if random.random() < 0.4 and g["lights"]:
        l = random.choice(g["lights"])
        l.x, l.y = random.randint(0, N-1), random.randint(0, N-1)

    if random.random() < 0.4 and g["blocks"]:
        b = random.choice(g["blocks"])
        b.s = 1 - b.s

    if random.random() < 0.2:
        g["hamster"] = (random.randint(0, N-1), random.randint(0, N-1))

    return g

# =========================
# CROSSOVER
# =========================

def crossover(a, b):
    c = copy.deepcopy(a)

    if random.random() < 0.5:
        c["lights"] = copy.deepcopy(b["lights"])
    if random.random() < 0.5:
        c["blocks"] = copy.deepcopy(b["blocks"])

    return c

# =========================
# SOLVER
# =========================

def solve():

    pop = [random_grid() for _ in range(POP_SIZE)]

    best = None
    best_score = 0

    for gen in range(GENERATIONS):

        scored = [(simulate(g), g) for g in pop]
        scored.sort(reverse=True, key=lambda x: x[0])

        if scored[0][0] > best_score:
            best_score = scored[0][0]
            best = scored[0][1]
            print(f"GEN {gen} BEST = {best_score}")

        survivors = [g for _, g in scored[:POP_SIZE//3]]

        new_pop = survivors[:]

        while len(new_pop) < POP_SIZE:
            a, b = random.sample(survivors, 2)
            child = crossover(a, b)
            if random.random() < MUTATION_RATE:
                child = mutate(child)
            new_pop.append(child)

        pop = new_pop

    return best, best_score

# =========================
# EXPORT
# =========================

def export(g):
    lines = []
    lines.append(str(N))
    lines.append(f"({g['hamster'][0]}, {g['hamster'][1]})")

    for l in g["lights"]:
        lines.append(f"L ({l.x}, {l.y}) {l.r}")
    for b in g["blocks"]:
        lines.append(f"B ({b.x}, {b.y}) {b.g} {b.s}")
    for s in g["switches"]:
        lines.append(f"S ({s.x}, {s.y}) {s.g}")

    return "\n".join(lines)

# =========================
# RUN
# =========================

if __name__ == "__main__":
    best, score = solve()

    print("FINAL SCORE:", score)

    with open("10_challenge1.txt", "w") as f:
        f.write(export(best))
