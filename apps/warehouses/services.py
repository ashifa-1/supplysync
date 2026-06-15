import random
import string

from django.db.models import Sum

from apps.inventory.models import Inventory
from core.exceptions import (
    ResourceNotFoundException,
    DuplicateResourceException,
    WarehouseHasActiveInventoryException,
    InvalidOperationException,
)

from .models import Warehouse


def generate_warehouse_code() -> str:
    while True:
        code = (
            "WH-"
            + "".join(
                random.choices(
                    string.ascii_uppercase
                    + string.digits,
                    k=6,
                )
            )
        )

        if not Warehouse.objects.filter(
            warehouse_code=code
        ).exists():
            return code


def create_warehouse(data: dict) -> Warehouse:
    warehouse_code = data.get("warehouse_code")

    if warehouse_code:
        if Warehouse.objects.filter(
            warehouse_code=warehouse_code
        ).exists():
            raise DuplicateResourceException(
                "Warehouse code already exists"
            )
    else:
        data["warehouse_code"] = generate_warehouse_code()

    return Warehouse.objects.create(**data)


def get_warehouse_by_id(warehouse_id: int) -> Warehouse:
    try:
        return Warehouse.objects.get(id=warehouse_id)
    except Warehouse.DoesNotExist:
        raise ResourceNotFoundException(
            "Warehouse not found"
        )


def get_warehouse_with_summary(warehouse_id: int) -> dict:
    warehouse = get_warehouse_by_id(warehouse_id)

    inventory = Inventory.objects.filter(warehouse=warehouse)
    total_distinct_products = inventory.count()
    total_quantity_available = (
        inventory.aggregate(total=Sum("quantity_available"))["total"]
        or 0
    )

    return {
        "id": warehouse.id,
        "warehouse_code": warehouse.warehouse_code,
        "name": warehouse.name,
        "location": warehouse.location,
        "city": warehouse.city,
        "state": warehouse.state,
        "pincode": warehouse.pincode,
        "capacity": warehouse.capacity,
        "is_active": warehouse.is_active,
        "total_distinct_products": total_distinct_products,
        "total_quantity_available": total_quantity_available,
    }


def update_warehouse(warehouse_id: int, data: dict) -> Warehouse:
    warehouse = get_warehouse_by_id(warehouse_id)

    if "warehouse_code" in data:
        raise InvalidOperationException(
            "Warehouse code cannot be changed",
            code="WAREHOUSE_CODE_IMMUTABLE"
        )

    for field, value in data.items():
        setattr(warehouse, field, value)

    warehouse.save()
    return warehouse


def delete_warehouse(warehouse_id: int) -> None:
    warehouse = get_warehouse_by_id(warehouse_id)

    has_inventory = (
        Inventory.objects.filter(
            warehouse=warehouse,
            quantity_available__gt=0,
        ).exists()
        or Inventory.objects.filter(
            warehouse=warehouse,
            quantity_reserved__gt=0,
        ).exists()
    )

    if has_inventory:
        raise WarehouseHasActiveInventoryException(
            "Warehouse has active inventory"
        )

    warehouse.delete()
