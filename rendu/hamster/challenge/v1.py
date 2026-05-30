import copy

# =========================
# CONFIG
# =========================

MAX_STEPS = 5000

# =========================
# STRUCTURES
# =========================

class Light:
    def __init__(self, x, y, r):
        self.x = x
        self.y = y
        self.r = r


class Block:
    def __init__(self, x, y, g, s):
        self.x = x
        self.y = y
        self.g = g
        self.s = s


class Switch:
    def __init__(self, x, y, g):
        self.x = x
        self.y = y
        self.g = g


# =========================
# UTILS
# =========================

def sign(a):
    return (a > 0) - (a < 0)


# =========================
# PARSER
# =========================

def parse_file(filename):

    with open(filename, "r") as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    N = int(lines[0])

    # hamster ignoré
    # ligne 1 = "(x, y)"
    # on l'utilise pas

    lights = []
    blocks = []
    switches = []

    occupied = set()

    for line in lines[2:]:

        parts = line.split()

        # =========================
        # LIGHT
        # =========================
        if line.startswith("L"):

            x = int(parts[1][1:-1].split(",")[0])
            y = int(parts[2][:-1])

            r = int(parts[3])

            lights.append(Light(x, y, r))
            occupied.add((x, y))

        # =========================
        # BLOCK
        # =========================
        elif line.startswith("B"):

            x = int(parts[1][1:-1].split(",")[0])
            y = int(parts[2][:-1])

            g = int(parts[3])
            s = int(parts[4])

            blocks.append(Block(x, y, g, s))
            occupied.add((x, y))

        # =========================
        # SWITCH
        # =========================
        elif line.startswith("S"):

            x = int(parts[1][1:-1].split(",")[0])
            y = int(parts[2][:-1])

            g = int(parts[3])

            switches.append(Switch(x, y, g))
            occupied.add((x, y))

    return {
        "N": N,
        "lights": lights,
        "blocks": blocks,
        "switches": switches,
        "occupied": occupied
    }


# =========================
# VISIBILITY
# =========================

def ray_visible(grid, x, y, light):

    dx = light.x - x
    dy = light.y - y

    # pas même ligne/colonne
    if dx != 0 and dy != 0:
        return False

    dist = abs(dx + dy)

    if dist > light.r:
        return False

    step_x = sign(dx)
    step_y = sign(dy)

    cx = x + step_x
    cy = y + step_y

    while (cx, cy) != (light.x, light.y):

        # blocs actifs
        for b in grid["blocks"]:
            if b.x == cx and b.y == cy and b.s == 1:
                return False

        # autres lumières
        for l in grid["lights"]:
            if l.x == cx and l.y == cy:
                return False

        cx += step_x
        cy += step_y

    return True


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


# =========================
# SIMULATION
# =========================

def simulate(grid, hamster_pos):

    local_grid = copy.deepcopy(grid)

    N = local_grid["N"]

    x, y = hamster_pos

    dx, dy = 0, 0

    steps = 0

    visited = set()

    for _ in range(MAX_STEPS):

        state = (x, y, dx, dy)

        if state in visited:
            return 0

        visited.add(state)

        visible = get_visible_lights(local_grid, x, y)

        # 2 lumières visibles = stop
        if len(visible) >= 2:
            return steps

        # 1 lumière = direction opposée
        if len(visible) == 1:
            dx, dy = visible[0]

        # aucune lumière
        else:
            if dx == 0 and dy == 0:
                return steps

        nx = x + dx
        ny = y + dy

        # hors grille
        if not (0 <= nx < N and 0 <= ny < N):
            return steps

        # collision blocs actifs
        blocked = False

        for b in local_grid["blocks"]:
            if b.x == nx and b.y == ny and b.s == 1:
                blocked = True
                break

        if blocked:
            return steps

        # collision lumières
        for l in local_grid["lights"]:
            if l.x == nx and l.y == ny:
                blocked = True
                break

        if blocked:
            return steps

        # switches
        for s in local_grid["switches"]:
            if s.x == nx and s.y == ny:

                for b in local_grid["blocks"]:
                    if b.g == s.g:
                        b.s = 1 - b.s

        x = nx
        y = ny

        steps += 1

    return 0


# =========================
# TEST
# =========================

def test(namefile):

    grid = parse_file(namefile)

    N = grid["N"]

    best_score = -1
    best_positions = []

    # toutes les cases libres
    for x in range(N):
        for y in range(N):

            if (x, y) in grid["occupied"]:
                continue

            score = simulate(grid, (x, y))

            print(f"TEST ({x}, {y}) => {score}")

            if score > best_score:
                best_score = score
                best_positions = [(x, y)]

            elif score == best_score:
                best_positions.append((x, y))

    print("\n========================")
    print("BEST SCORE:", best_score)
    print("BEST POSITIONS:")

    for pos in best_positions:
        print(pos)

    return best_positions, best_score


# =========================
# RUN
# =========================

if __name__ == "__main__":

    test("10_challenge3_1.txt")