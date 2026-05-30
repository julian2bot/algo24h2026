import sys
from typing import List, Tuple

def main():
    # --- Lecture des données initiales ---
    n_items = int(sys.stdin.readline().split()[1])
    size_capacity = int(sys.stdin.readline().split()[1])
    weight_capacity = int(sys.stdin.readline().split()[1])

    items: List[Tuple[int, int, int, int]] = []  # (id, taille, poids, valeur)
    for _ in range(n_items):
        data = list(map(int, sys.stdin.readline().split()))
        items.append((data[0], data[1], data[2], data[3]))

    # --- Pré-traitement : tri par ratio valeur/(taille+poids) ---
    items.sort(key=lambda x: x[3] / (x[1] + x[2]), reverse=True)

    # --- Variables de suivi ---
    available_items = items.copy()
    my_size = 0
    my_weight = 0
    opponent_size = 0  # Non utilisé ici, mais utile pour une stratégie avancée
    opponent_weight = 0

    # Attendre la fin du pré-traitement
    sys.stdin.readline()  # "preprocessing 5000"

    # --- Boucle de jeu ---
    while True:
        # Lire l'objet pris par l'adversaire
        taken_line = sys.stdin.readline().strip()
        if not taken_line.startswith("taken"):
            break  # Fin de la partie
        taken_id = int(taken_line.split()[1])

        # Mettre à jour la liste des objets disponibles
        if taken_id != -1:
            available_items = [item for item in available_items if item[0] != taken_id]

        # Lire le temps restant pour ce tour
        next_line = sys.stdin.readline().strip()
        if not next_line.startswith("next_item"):
            break

        # --- Choix de l'objet ---
        best_item = None
        best_ratio = -1.0

        for item in available_items:
            item_id, item_size, item_weight, item_value = item
            # Vérifier si l'objet peut être pris
            if (my_size + item_size <= size_capacity) and (my_weight + item_weight <= weight_capacity):
                ratio = item_value / (item_size + item_weight)
                if ratio > best_ratio:
                    best_ratio = ratio
                    best_item = item

        # Si aucun objet ne peut être pris, passer
        if best_item is None:
            print(-1)
            sys.stdout.flush()
            break

        # Prendre l'objet
        item_id, item_size, item_weight, item_value = best_item
        my_size += item_size
        my_weight += item_weight
        available_items.remove(best_item)

        print(item_id)
        sys.stdout.flush()

if __name__ == "__main__":
    main()