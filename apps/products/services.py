import random
import string

from apps.inventory.models import Inventory
from .models import Product
from core.exceptions import ResourceNotFoundException


def generate_sku(category_code: str) -> str:
    category_code = category_code.replace("CAT-", "")

    while True:
        sku = (
            f"SKU-{category_code}-"
            + "".join(
                random.choices(
                    string.ascii_uppercase
                    + string.digits,
                    k=8,
                )
            )
        )

        if not Product.objects.filter(sku=sku).exists():
            return sku


def create_product(data: dict) -> Product:
    if not data.get("sku"):
        data["sku"] = generate_sku(
            data["category"].category_code
        )

    return Product.objects.create(**data)


def get_product_with_inventory(product_id: int) -> dict:
    try:
        product = Product.objects.get(id=product_id)
    except Product.DoesNotExist:
        raise ResourceNotFoundException(
            "Product not found"
        )

    inventory = Inventory.objects.filter(product=product)

    inventory_by_warehouse = [
        {
            "warehouse_id": item.warehouse.id,
            "warehouse_name": item.warehouse.name,
            "quantity_available": item.quantity_available,
            "quantity_reserved": item.quantity_reserved,
        }
        for item in inventory
    ]

    return {
        "id": product.id,
        "sku": product.sku,
        "name": product.name,
        "description": product.description,
        "category": product.category.id,
        "unit_price": product.unit_price,
        "unit_of_measure": product.unit_of_measure,
        "reorder_level": product.reorder_level,
        "is_active": product.is_active,
        "inventory_by_warehouse": inventory_by_warehouse,
    }