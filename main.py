import random

def main():
    strs = input().split()
    assert(strs[0] == "n_items" and len(strs) == 2)
    n_items = int(strs[1])
    
    strs = input().split()
    assert(strs[0] == "size_capacity" and len(strs) == 2)
    size_capacity = int(strs[1])
        
    strs = input().split()
    assert(strs[0] == "weight_capacity" and len(strs) == 2)
    weight_capacity = int(strs[1])

    items = []

    for i in range(n_items):
        strs = input().split()
        assert(len(strs) == 4)
        # TODO enregistrer les informations sur les objets (ici on utilise un simple tuple)
        items.append((int(strs[0]), int(strs[1]), int(strs[2]), int(strs[3])))

    strs = input().split()
    assert(strs[0] == "preprocessing" and len(strs) == 2)
    preprocessing_time = int(strs[1])

    # TODO calculs préliminaires

    while(True):
        strs = input().split()
        assert(strs[0] == "taken" and len(strs) == 2)
        taken = int(strs[1])

        # TODO mettre à jour les informations sur les objets disponibles

        strs = input().split()
        assert(strs[0] == "next_item" and len(strs) == 2)
        processing_time = int(strs[1])

        # TODO choisir un objet        
        item = random.randrange(n_items)

        print(item)
     


if __name__ == "__main__":
    main()
