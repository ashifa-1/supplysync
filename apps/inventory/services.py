from django.db import transaction

from apps.products.models import Product
from apps.warehouses.models import Warehouse

import uuid

from django.db.models import F
from django.core.cache import cache

from .tasks import (
    process_inventory_transfer_event,
)

from .models import (
    Inventory,
    InventoryTransaction,
    TransactionType,
)

from core.exceptions import (
    InsufficientInventoryException,
)

from .tasks import (
    process_inventory_updated_event,
)


def get_low_stock_alerts():
    cached_data = cache.get(
        "inventory:low-stock"
    )

    if cached_data:
        return cached_data

    inventory_items = (
        Inventory.objects.filter(
            quantity_available__lte=
            F(
                "product__reorder_level"
            )
        )
    )

    alerts = []

    for item in inventory_items:
        alerts.append(
            {
                "product_id":
                    item.product.id,
                "sku":
                    item.product.sku,
                "product_name":
                    item.product.name,
                "warehouse_id":
                    item.warehouse.id,
                "warehouse_name":
                    item.warehouse.name,
                "quantity_available":
                    item.quantity_available,
                "reorder_level":
                    item.product.reorder_level,
                "deficit":
                    (
                        item.product.reorder_level
                        -
                        item.quantity_available
                    ),
            }
        )

    cache.set(
        "inventory:low-stock",
        alerts,
        timeout=300
    )

    return alerts

@transaction.atomic
def adjust_inventory(
    data,
    performed_by_user_id
):
    product = Product.objects.get(
        id=data["product_id"]
    )

    warehouse = Warehouse.objects.get(
        id=data["warehouse_id"]
    )

    inventory, _ = (
        Inventory.objects.get_or_create(
            product=product,
            warehouse=warehouse,
            defaults={
                "quantity_available": 0,
                "quantity_reserved": 0,
                "quantity_damaged": 0,
            },
        )
    )

    transaction_type = data[
        "transaction_type"
    ]

    quantity = data["quantity"]

    if (
        transaction_type
        == TransactionType.INBOUND
    ):
        inventory.quantity_available += (
            quantity
        )

    elif (
        transaction_type
        == TransactionType.OUTBOUND
    ):
        if (
            inventory.quantity_available
            < quantity
        ):
            raise (
                InsufficientInventoryException()
            )

        inventory.quantity_available -= (
            quantity
        )

    elif (
        transaction_type
        == TransactionType.DAMAGE_REPORT
    ):
        if (
            inventory.quantity_available
            < quantity
        ):
            raise (
                InsufficientInventoryException()
            )

        inventory.quantity_available -= (
            quantity
        )

        inventory.quantity_damaged += (
            quantity
        )

    elif (
        transaction_type
        == TransactionType.ADJUSTMENT
    ):
        inventory.quantity_available += (
            quantity
        )

        if (
            inventory.quantity_available
            < 0
        ):
            raise (
                InsufficientInventoryException()
            )

    inventory.save()

    inventory_transaction = (
        InventoryTransaction.objects.create(
            product=product,
            warehouse=warehouse,
            transaction_type=transaction_type,
            quantity=quantity,
            performed_by_id=(
                performed_by_user_id
            ),
            notes=data.get(
                "notes",
                "",
            ),
        )
    )

    process_inventory_updated_event.delay(
        inventory_transaction.id
    )

    return inventory_transaction



@transaction.atomic
def transfer_inventory(
    data,
    performed_by_user_id
):
    source_inventory = (
        Inventory.objects.select_for_update()
        .get(
            product_id=data["product_id"],
            warehouse_id=data[
                "source_warehouse_id"
            ],
        )
    )

    destination_inventory, _ = (
        Inventory.objects.select_for_update()
        .get_or_create(
            product_id=data["product_id"],
            warehouse_id=data[
                "destination_warehouse_id"
            ],
            defaults={
                "quantity_available": 0,
                "quantity_reserved": 0,
                "quantity_damaged": 0,
            },
        )
    )

    quantity = data["quantity"]

    if (
        source_inventory.quantity_available
        < quantity
    ):
        raise (
            InsufficientInventoryException()
        )

    source_inventory.quantity_available -= (
        quantity
    )

    destination_inventory.quantity_available += (
        quantity
    )

    source_inventory.save()

    destination_inventory.save()

    reference_id = (
        "TRANSFER-"
        + str(uuid.uuid4())[:8]
    )

    InventoryTransaction.objects.create(
        product_id=data["product_id"],
        warehouse_id=data[
            "source_warehouse_id"
        ],
        transaction_type=
            TransactionType.OUTBOUND,
        quantity=quantity,
        reference_id=reference_id,
        performed_by_id=
            performed_by_user_id,
        notes=data.get(
            "notes",
            "",
        ),
    )

    InventoryTransaction.objects.create(
        product_id=data["product_id"],
        warehouse_id=data[
            "destination_warehouse_id"
        ],
        transaction_type=
            TransactionType.INBOUND,
        quantity=quantity,
        reference_id=reference_id,
        performed_by_id=
            performed_by_user_id,
        notes=data.get(
            "notes",
            "",
        ),
    )

    process_inventory_transfer_event.delay(
        reference_id
    )

    return {
        "reference_id":
            reference_id
    }




def get_warehouse_inventory(
    warehouse_id
):
    return Inventory.objects.filter(
        warehouse_id=warehouse_id
    )