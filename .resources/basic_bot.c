#include <stdio.h>
#include <stdlib.h>

struct item {
  int id;
  int size;
  int weight;
  int value;
};

int main() {
  int n_items, size_capacity, weight_capacity, preprocessing_time;

  scanf("n_items %d%*c", &n_items);
  scanf("size_capacity %d%*c", &size_capacity);
  scanf("weight_capacity %d%*c", &weight_capacity);

  struct item* items = malloc(n_items * sizeof(struct item));

  for (int i = 0; i < n_items; i++) {
    scanf("%d %d %d %d%*c", &items[i].id, &items[i].size, &items[i].weight, &items[i].value);
  }

  scanf("preprocessing %d%*c", &preprocessing_time);
  // ici: calculs préliminaires

  while (1) {
    int id;
    scanf("taken %d%*c", &id);
    
    // ici: mise à jour des informations sur l'objet pris par l'adversaire

    int turn_time;
    scanf("next_item %d%*c", &turn_time);

    // ici: choisir un objet
    int item = rand() % n_items;
    
    printf("%d\n", item);
    fflush(stdout);
  }

  return 0;

}
