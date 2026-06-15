import uuid
import logging

from django.db import transaction
from django.db.models import F
from django.core.cache import cache

from apps.products.models import Product
from apps.warehouses.models import Warehouse
from .models import (
    Inventory,
    InventoryTransaction,
    TransactionType,
)
from core.exceptions import (
    InsufficientInventoryException,
    InvalidOperationException,
)
from core.constants import (
    INVENTORY_LOW_STOCK_KEY,
    INVENTORY_LOW_STOCK_TTL,
)

logger = logging.getLogger(__name__)


def get_low_stock_alerts() -> list:
    cached_data = cache.get(INVENTORY_LOW_STOCK_KEY)
    if cached_data is not None:
        return cached_data

    inventory_items = Inventory.objects.filter(
        quantity_available__lte=F("product__reorder_level")
    ).select_related("product", "warehouse")

    alerts = [
        {
            "product_id": item.product.id,
            "sku": item.product.sku,
            "product_name": item.product.name,
            "warehouse_id": item.warehouse.id,
            "warehouse_name": item.warehouse.name,
            "quantity_available": item.quantity_available,
            "reorder_level": item.product.reorder_level,
            "deficit": item.product.reorder_level - item.quantity_available,
        }
        for item in inventory_items
    ]

    cache.set(INVENTORY_LOW_STOCK_KEY, alerts, timeout=INVENTORY_LOW_STOCK_TTL)
    return alerts


@transaction.atomic
def adjust_inventory(data: dict, performed_by_user_id: int):
    product = Product.objects.get(id=data["product_id"])
    warehouse = Warehouse.objects.get(id=data["warehouse_id"])

    inventory, _ = Inventory.objects.get_or_create(
        product=product,
        warehouse=warehouse,
        defaults={
            "quantity_available": 0,
            "quantity_reserved": 0,
            "quantity_damaged": 0,
        },
    )

    transaction_type = data["transaction_type"]
    quantity = data["quantity"]

    if transaction_type == TransactionType.INBOUND:
        inventory.quantity_available += quantity
    elif transaction_type == TransactionType.OUTBOUND:
        if inventory.quantity_available < quantity:
            raise InsufficientInventoryException(
                detail="Insufficient inventory"
            )
        inventory.quantity_available -= quantity
    elif transaction_type == TransactionType.DAMAGE_REPORT:
        if inventory.quantity_available < quantity:
            raise InsufficientInventoryException(
                detail="Insufficient inventory"
            )
        inventory.quantity_available -= quantity
        inventory.quantity_damaged += quantity
    elif transaction_type == TransactionType.ADJUSTMENT:
        inventory.quantity_available += quantity
        if inventory.quantity_available < 0:
            raise InsufficientInventoryException(
                detail="Insufficient inventory"
            )
    else:
        raise InvalidOperationException(
            detail="Invalid transaction type"
        )

    inventory.save()

    inventory_transaction = InventoryTransaction.objects.create(
        product=product,
        warehouse=warehouse,
        transaction_type=transaction_type,
        quantity=quantity,
        performed_by_id=performed_by_user_id,
        notes=data.get("notes", ""),
    )

    cache.delete(INVENTORY_LOW_STOCK_KEY)

    from .tasks import process_inventory_updated_event

    process_inventory_updated_event.delay(
        inventory_transaction.id
    )

    return inventory_transaction


@transaction.atomic
def transfer_inventory(data: dict, performed_by_user_id: int) -> dict:
    source_inventory = Inventory.objects.select_for_update().get(
        product_id=data["product_id"],
        warehouse_id=data["source_warehouse_id"],
    )

    destination_inventory, _ = Inventory.objects.select_for_update().get_or_create(
        product_id=data["product_id"],
        warehouse_id=data["destination_warehouse_id"],
        defaults={
            "quantity_available": 0,
            "quantity_reserved": 0,
            "quantity_damaged": 0,
        },
    )

    quantity = data["quantity"]

    if source_inventory.quantity_available < quantity:
        raise InsufficientInventoryException(
            detail="Insufficient inventory"
        )

    source_inventory.quantity_available -= quantity
    destination_inventory.quantity_available += quantity

    source_inventory.save()
    destination_inventory.save()

    reference_id = f"TRANSFER-{uuid.uuid4().hex[:8]}"

    InventoryTransaction.objects.create(
        product_id=data["product_id"],
        warehouse_id=data["source_warehouse_id"],
        transaction_type=TransactionType.OUTBOUND,
        quantity=quantity,
        reference_id=reference_id,
        performed_by_id=performed_by_user_id,
        notes=data.get("notes", ""),
    )

    InventoryTransaction.objects.create(
        product_id=data["product_id"],
        warehouse_id=data["destination_warehouse_id"],
        transaction_type=TransactionType.INBOUND,
        quantity=quantity,
        reference_id=reference_id,
        performed_by_id=performed_by_user_id,
        notes=data.get("notes", ""),
    )

    cache.delete(INVENTORY_LOW_STOCK_KEY)

    from .tasks import process_inventory_transfer_event

    process_inventory_transfer_event.delay(
        reference_id
    )

    return {"reference_id": reference_id}


def get_warehouse_inventory(warehouse_id: int):
    return Inventory.objects.filter(warehouse_id=warehouse_id)
