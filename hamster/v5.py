import random
import copy

# =========================
# CONFIG
# =========================

N = 10  # 10 ou 50
POP_SIZE = 400
GENERATIONS = 1000
MUTATION_RATE = 0.1

# =========================
# STRUCTURES
# =========================

class Light:
    def __init__(self, x, y, r):
        self.x, self.y, self.r = x, y, r

class Block:
    def __init__(self, x, y, g, s):
        self.x, self.y, self.g, self.s = x, y, g, s

class Switch:
    def __init__(self, x, y, g):
        self.x, self.y, self.g = x, y, g


# =========================
# UTIL
# =========================

def in_bounds(x, y):
    return 0 <= x < N and 0 <= y < N


# =========================
# SIMULATION (VERSION FIDÈLE SIMPLIFIÉE)
# =========================
def get_visible_lights(grid, x, y):
    visible = []

    for l in grid["lights"]:
        if ray_visible(grid, x, y, l):
            dx = l.x - x
            dy = l.y - y

            if dx != 0:
                direction = (-sign(dx), 0)
            else:
                direction = (0, -sign(dy))

            visible.append(direction)

    return visible

def sign(a):
    return (a > 0) - (a < 0)


def ray_visible(grid, x, y, light):
    """
    Vérifie si une lumière voit le hamster
    + respecte blocage par blocs actifs + autres lumières
    """

    dx = light.x - x
    dy = light.y - y

    # même ligne ou colonne uniquement
    if dx != 0 and dy != 0:
        return False

    dist = abs(dx + dy)
    if dist > light.r:
        return False

    step_x = sign(dx)
    step_y = sign(dy)

    cx, cy = x + step_x, y + step_y

    while (cx, cy) != (light.x, light.y):

        # bloc actif bloque la vision
        for b in grid["blocks"]:
            if b.x == cx and b.y == cy and b.s == 1:
                return False

        # lumière r=0 ou autre lumière bloque vision
        for l in grid["lights"]:
            if l.x == cx and l.y == cy:
                return False

        cx += step_x
        cy += step_y

    return True

def visible_light(x, y, lights, blocks):
    """Retourne nb de lumières visibles + direction"""
    visibles = []

    for l in lights:
        dx = l.x - x
        dy = l.y - y

        if dx != 0 and dy != 0:
            continue

        dist = abs(dx + dy)
        if dist > l.r:
            continue

        # check obstruction
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)

        cx, cy = x + step_x, y + step_y
        blocked = False

        while (cx, cy) != (l.x, l.y):
            for b in blocks:
                if b.x == cx and b.y == cy and b.s == 1:
                    blocked = True
            for other in lights:
                if other.x == cx and other.y == cy and other != l:
                    blocked = True

            if blocked:
                break

            cx += step_x
            cy += step_y

        if not blocked:
            visibles.append((step_x, step_y))

    return visibles


# =========================
# SCORE SIMULATION
# =========================

def simulate(grid):
    x, y = grid["hamster"]

    dx, dy = 0, 0  # IMMOBILE AU DÉBUT

    steps = 0
    visited = set()

    for _ in range(5000):

        state = (x, y, dx, dy)
        if state in visited:
            return 0
        visited.add(state)

        visible = get_visible_lights(grid, x, y)

        # CAS 2+ lumières → mort immédiate
        if len(visible) >= 2:
            return steps

        # CAS 1 lumière → prend direction opposée
        if len(visible) == 1:
            dx, dy = visible[0]

        # CAS 0 lumière
        else:
            if dx == 0 and dy == 0:
                return steps  # immobile + rien → stop

        nx, ny = x + dx, y + dy

        # hors grille
        if not (0 <= nx < N and 0 <= ny < N):
            return steps

        # bloc actif bloque déplacement
        for b in grid["blocks"]:
            if b.x == nx and b.y == ny and b.s == 1:
                return steps

        # lumière bloque déplacement (toujours)
        for l in grid["lights"]:
            if l.x == nx and l.y == ny:
                return steps

        # switch (toggle blocs)
        for s in grid["switches"]:
            if s.x == nx and s.y == ny:
                for b in grid["blocks"]:
                    if b.g == s.g:
                        b.s = 1 - b.s

        x, y = nx, ny
        steps += 1

    return 0

    
# =========================
# GENERATION INITIALE
# =========================

def random_grid():
    cells = [(x, y) for x in range(N) for y in range(N)]

    hamster = random.choice(cells)
    cells.remove(hamster)

    lights = []
    blocks = []
    switches = []

    for _ in range(random.randint(2, 5)):
        if not cells: break
        x, y = random.choice(cells)
        cells.remove((x, y))
        lights.append(Light(x, y, random.randint(1, N)))

    for _ in range(random.randint(3, 10)):
        if not cells: break
        x, y = random.choice(cells)
        cells.remove((x, y))
        blocks.append(Block(x, y, random.randint(0, 5), random.randint(0, 1)))

    for _ in range(random.randint(1, 4)):
        if not cells: break
        x, y = random.choice(cells)
        cells.remove((x, y))
        switches.append(Switch(x, y, random.randint(0, 5)))

    return {
        "hamster": hamster,
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
        l.r = random.randint(1, N)

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
    child = copy.deepcopy(a)

    if random.random() < 0.5:
        child["lights"] = copy.deepcopy(b["lights"])
    if random.random() < 0.5:
        child["blocks"] = copy.deepcopy(b["blocks"])

    return child


# =========================
# ENCODAGE EXPORT
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
# ALGO GÉNÉTIQUE
# =========================

def solve():
    population = [random_grid() for _ in range(POP_SIZE)]

    best = None
    best_score = 0

    for gen in range(GENERATIONS):

        scored = []
        for g in population:
            score = simulate(g)
            scored.append((score, g))

        scored.sort(reverse=True, key=lambda x: x[0])

        if scored[0][0] > best_score:
            best_score = scored[0][0]
            best = scored[0][1]
            print(f"[GEN {gen}] NEW BEST => {best_score}")

        # sélection top 30%
        survivors = [g for _, g in scored[:POP_SIZE // 3]]

        # nouvelle population
        new_pop = survivors[:]

        while len(new_pop) < POP_SIZE:
            a, b = random.sample(survivors, 2)
            child = crossover(a, b)
            if random.random() < MUTATION_RATE:
                child = mutate(child)
            new_pop.append(child)

        population = new_pop

    return best, best_score


# =========================
# RUN + EXPORT FINAL
# =========================

if __name__ == "__main__":
    best_grid, score = solve()

    print("FINAL SCORE:", score)

    txt = export(best_grid)

    with open(f"{N}_c{score}.txt", "w") as f:
        f.write(txt)

    print("EXPORTED:", f"{N}_c{score}.txt")
