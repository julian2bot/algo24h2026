import random

N = 10

# =========================
# STRUCTURE : ZIGZAG FLOW
# =========================

def build_zigzag():

    grid = {
        "hamster": (1, 1),
        "lights": [],
        "blocks": [],
        "switches": []
    }

    direction = 1

    for y in range(1, N-1):

        if direction == 1:
            for x in range(1, N-1):
                if x % 3 == 0:
                    grid["lights"].append(L(x, y, N))
        else:
            for x in range(N-2, 0, -1):
                if x % 3 == 0:
                    grid["lights"].append(L(x, y, N))

        # murs directionnels (bloque fuite)
        grid["blocks"].append(B(0, y, 0, 1))
        grid["blocks"].append(B(N-1, y, 0, 1))

        direction *= -1

    return grid


# =========================
# STRUCTURE : CORRIDOR LINEAIRE
# =========================

def build_corridor():

    grid = {
        "hamster": (1, N//2),
        "lights": [],
        "blocks": [],
        "switches": []
    }

    y = N//2

    # ligne de lumière contrôlée
    for x in range(2, N-2):
        if x % 2 == 0:
            grid["lights"].append(L(x, y, N))

    # murs latéraux
    for y2 in range(N):
        grid["blocks"].append(B(0, y2, 0, 1))
        grid["blocks"].append(B(N-1, y2, 0, 1))

    return grid


# =========================
# STRUCTURE : LOOP CONTROLLED
# =========================

def build_loop():

    grid = {
        "hamster": (1, 1),
        "lights": [],
        "blocks": [],
        "switches": []
    }

    # carré intérieur
    for i in range(1, N-1):

        grid["lights"].append(L(i, 1, N))
        grid["lights"].append(L(N-2, i, N))
        grid["lights"].append(L(i, N-2, N))
        grid["lights"].append(L(1, i, N))

    # bloque sorties
    for i in range(N):
        grid["blocks"].append(B(i, 0, 0, 1))
        grid["blocks"].append(B(i, N-1, 0, 1))
        grid["blocks"].append(B(0, i, 0, 1))
        grid["blocks"].append(B(N-1, i, 0, 1))

    return grid


# =========================
# OBJETS
# =========================

class L:
    def __init__(self,x,y,r):
        self.x=x; self.y=y; self.r=r

class B:
    def __init__(self,x,y,g,s):
        self.x=x; self.y=y; self.g=g; self.s=s


# =========================
# GENERATEUR FINAL
# =========================

def generate_best():

    designs = [
        build_zigzag(),
        build_corridor(),
        build_loop()
    ]

    return random.choice(designs)


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


if __name__ == "__main__":
    g = generate_best()
    print(export(g))
    
