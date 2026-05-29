from item import Item


class Inventory:
    def __init__(self, n_items: int, size_capacity: int, weight_capacity: int, preprocessing_time: int, items: tuple[Item]) -> None:
        self.n_items= n_items
        self.size_capacity = size_capacity
        self.weight_capacity = weight_capacity
        self.preprocessing_time = preprocessing_time
        self.items = items

        self.inventory: list[Item] = []
        self.inventory_size: int = 0
        self.inventory_weight = 0

    def add_items(self, item: Item) -> bool:
        new_inventory_size = self.inventory_size + item.size
        new_inventory_weight = self.inventory_weight + item.weight
        
        if new_inventory_size > self.size_capacity or new_inventory_weight > self.weight_capacity:
            return False
        else:
            self.inventory.append(item)
            self.inventory_size = new_inventory_size
            self.inventory_weight = new_inventory_weight
            return True
        


