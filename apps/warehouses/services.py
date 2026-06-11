from .models import Warehouse

from core.exceptions import (
    ResourceNotFoundException,
)
from django.db.models import Sum

from apps.inventory.models import (
    Inventory,
)
import random
import string

from .models import Warehouse

from core.exceptions import (
    ResourceNotFoundException,
)


def generate_warehouse_code():
    while True:
        code = (
            "WH-"
            + "".join(
                random.choices(
                    string.ascii_uppercase
                    + string.digits,
                    k=6
                )
            )
        )

        if not Warehouse.objects.filter(
            warehouse_code=code
        ).exists():
            return code


def create_warehouse(data):
    if not data.get(
        "warehouse_code"
    ):
        data[
            "warehouse_code"
        ] = generate_warehouse_code()

    return Warehouse.objects.create(
        **data
    )

def get_warehouse_by_id(
    warehouse_id
):
    try:
        return Warehouse.objects.get(
            id=warehouse_id
        )
    except Warehouse.DoesNotExist:
        raise ResourceNotFoundException(
            "Warehouse not found"
        )


def get_warehouse_with_summary(
    warehouse_id
):
    warehouse = get_warehouse_by_id(
        warehouse_id
    )

    inventory = Inventory.objects.filter(
        warehouse=warehouse
    )

    total_distinct_products = (
        inventory.count()
    )

    total_quantity_available = (
        inventory.aggregate(
            total=Sum(
                "quantity_available"
            )
        )["total"]
        or 0
    )

    return {
        "id": warehouse.id,
        "warehouse_code": (
            warehouse.warehouse_code
        ),
        "name": warehouse.name,
        "city": warehouse.city,
        "state": warehouse.state,
        "total_distinct_products":
            total_distinct_products,
        "total_quantity_available":
            total_quantity_available,
    }