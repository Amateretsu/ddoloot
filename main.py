#!/usr/bin/env python3
from packages.item import DDOItem, DDOItemType

def main():
    print("=== DDO Item Catalog Manager ===")

    # Example
    sword = DDOItem.create(
        name="Celestial Avenger",
        item_type=DDOItemType.WEAPON_LONG_SWORD  # ← SIMPLE!
    )

    print(f"Item: {sword.name}")
    print(f"Type: {sword.full_type}")  # Weapon Long Sword
    print(f"Dict: {sword.to_dict()}")

    # End - Example
ß

if __name__ == "__main__":
    main()