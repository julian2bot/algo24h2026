#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define MAX_N 50
#define MAX_L 200
#define MAX_B 200
#define MAX_S 50
#define MAX_STEPS 2000

// =========================
// STRUCTURES
// =========================

typedef struct {
    int x, y, r;
} Light;

typedef struct {
    int x, y, g, s;
} Block;

typedef struct {
    int x, y, g;
} Switch;

typedef struct {
    int x, y;
} Pos;

// =========================
// GLOBAL GRID
// =========================

int N;

Pos hamster;

Light lights[MAX_L];
Block blocks[MAX_B];
Switch switches[MAX_S];

int l_count = 0;
int b_count = 0;
int s_count = 0;

// =========================
// UTILS
// =========================

int sign(int a) {
    return (a > 0) - (a < 0);
}

int in_bounds(int x, int y) {
    return x >= 0 && y >= 0 && x < N && y < N;
}

// =========================
// VISIBILITE LUMIERE
// =========================

int ray_visible(int x, int y, Light *l) {

    int dx = l->x - x;
    int dy = l->y - y;

    if (dx != 0 && dy != 0) return 0;

    int dist = abs(dx + dy);
    if (dist > l->r) return 0;

    int sx = sign(dx);
    int sy = sign(dy);

    int cx = x + sx;
    int cy = y + sy;

    while (!(cx == l->x && cy == l->y)) {

        // blocs
        for (int i = 0; i < b_count; i++) {
            if (blocks[i].x == cx && blocks[i].y == cy && blocks[i].s == 1)
                return 0;
        }

        cx += sx;
        cy += sy;
    }

    return 1;
}

// =========================
// GET DIRECTION LIGHT
// =========================

int get_direction(int x, int y, int *dx, int *dy) {

    int count = 0;
    int tmp_dx = 0, tmp_dy = 0;

    for (int i = 0; i < l_count; i++) {

        if (ray_visible(x, y, &lights[i])) {

            int vx = lights[i].x - x;
            int vy = lights[i].y - y;

            if (vx != 0) {
                tmp_dx = -sign(vx);
                tmp_dy = 0;
            } else {
                tmp_dx = 0;
                tmp_dy = -sign(vy);
            }

            count++;
        }
    }

    if (count == 1) {
        *dx = tmp_dx;
        *dy = tmp_dy;
    }

    return count;
}

// =========================
// SIMULATION
// =========================
int simulate() {

    int x = hamster.x;
    int y = hamster.y;

    int dx = 0;
    int dy = 0;

    int steps = 0;

    for (int i = 0; i < MAX_STEPS; i++) {

        int vis_count = 0;

        int tmp_dx = 0;
        int tmp_dy = 0;

        // =========================
        // DETECTION LUMIERES
        // =========================
        for (int l = 0; l < l_count; l++) {

            Light *light = &lights[l];

            int vx = light->x - x;
            int vy = light->y - y;

            // pas même ligne/colonne
            if (vx != 0 && vy != 0)
                continue;

            int dist = abs(vx + vy);
            if (dist > light->r)
                continue;

            int sx = sign(vx);
            int sy = sign(vy);

            int cx = x + sx;
            int cy = y + sy;

            int blocked = 0;

            // check obstacles entre hamster et lumière
            while (!(cx == light->x && cy == light->y)) {

                // blocs actifs bloquent vision
                for (int b = 0; b < b_count; b++) {
                    if (blocks[b].x == cx &&
                        blocks[b].y == cy &&
                        blocks[b].s == 1) {
                        blocked = 1;
                        break;
                    }
                }

                if (blocked) break;

                cx += sx;
                cy += sy;
            }

            if (blocked) continue;

            // lumière visible
            vis_count++;

            tmp_dx = (vx != 0) ? -sign(vx) : 0;
            tmp_dy = (vy != 0) ? -sign(vy) : 0;
        }

        // =========================
        // REGLES DE DECISION
        // =========================

        if (vis_count >= 2)
            return steps;

        if (vis_count == 1) {
            dx = tmp_dx;
            dy = tmp_dy;
        }

        if (vis_count == 0) {
            if (dx == 0 && dy == 0)
                return steps;
            // sinon on continue direction actuelle
        }

        // =========================
        // DEPLACEMENT
        // =========================

        int nx = x + dx;
        int ny = y + dy;

        if (nx < 0 || ny < 0 || nx >= N || ny >= N)
            return steps;

        // collision blocs
        for (int b = 0; b < b_count; b++) {
            if (blocks[b].x == nx &&
                blocks[b].y == ny &&
                blocks[b].s == 1)
                return steps;
        }

        // déplacement
        x = nx;
        y = ny;
        steps++;
    }

    return 0;
}	
// =========================
// DESIGN SIMPLE (CORRIDOR)
// =========================
void build_corridor() {

    hamster.x = 1;
    hamster.y = N / 2;

    l_count = 0;
    b_count = 0;

    int y = N / 2;

    // 🔥 LUMIERE DE START OBLIGATOIRE
    lights[l_count++] = (Light){2, y, N};

    // chaîne directionnelle
    for (int x = 3; x < N - 2; x++) {
        if (x % 2 == 0) {
            lights[l_count++] = (Light){x, y, N};
        }
    }

    // murs latéraux (ok)
    for (int i = 0; i < N; i++) {
        blocks[b_count++] = (Block){0, i, 0, 1};
        blocks[b_count++] = (Block){N - 1, i, 0, 1};
    }
}

// =========================
// EXPORT
// =========================

void export_solution(int score) {

    char filename[64];
    sprintf(filename, "%d_c_%d.txt", N, score);

    FILE *f = fopen(filename, "w");

    fprintf(f, "%d\n", N);
    fprintf(f, "(%d, %d)\n", hamster.x, hamster.y);

    for (int i = 0; i < l_count; i++) {
        fprintf(f, "L (%d, %d) %d\n",
                lights[i].x,
                lights[i].y,
                lights[i].r);
    }

    for (int i = 0; i < b_count; i++) {
        fprintf(f, "B (%d, %d) %d %d\n",
                blocks[i].x,
                blocks[i].y,
                blocks[i].g,
                blocks[i].s);
    }

    for (int i = 0; i < s_count; i++) {
        fprintf(f, "S (%d, %d) %d\n",
                switches[i].x,
                switches[i].y,
                switches[i].g);
    }

    fclose(f);
}

// =========================
// MAIN
// =========================

int main() {

    srand(time(NULL));

    N = 10;

    build_corridor();

    int best_score = 0;

    for (int i = 0; i < 1000; i++) {

        int s = simulate();

        if (s > best_score)
            best_score = s;
    }

    export_solution(best_score);

    printf("BEST SCORE = %d\n", best_score);

    return 0;
}
