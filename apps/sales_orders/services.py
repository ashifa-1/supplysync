import uuid

from django.db import transaction
from django.utils import timezone
from django.db.models import F

from .models import (
    SalesOrder,
    SalesOrderItem,
    SalesOrderStatus,
)

from apps.inventory.models import Inventory
from apps.inventory.services import adjust_inventory
from apps.products.models import Product
from core.exceptions import (
    ResourceNotFoundException,
    InvalidOperationException,
    InsufficientStockException,
)


def _generate_order_number() -> str:
    return f"SO-{uuid.uuid4().hex[:8].upper()}"


@transaction.atomic
def create_sales_order(data, created_by_user_id):
    """
    Create sales order with stock reservation.
    Validates sufficient stock with select_for_update().
    """
    items = data.pop("items", [])

    if not items:
        raise InvalidOperationException(
            "Sales order must contain at least one item",
            code="SALES_ORDER_HAS_NO_ITEMS"
        )

    warehouse_id = data.get("warehouse")
    if hasattr(warehouse_id, "id"):
        warehouse_id = warehouse_id.id

    short_items = []

    for item_data in items:
        product_id = item_data["product"]
        if hasattr(product_id, "id"):
            product_id = product_id.id

        product = Product.objects.get(id=product_id)
        quantity = item_data["quantity"]

        inventory = (
            Inventory.objects
            .select_for_update()
            .filter(
                warehouse_id=warehouse_id,
                product=product,
            )
            .first()
        )

        if (
            not inventory 
            or inventory.quantity_available < quantity
        ):
            available = inventory.quantity_available if inventory else 0
            short_items.append({
                "product_id": product.id,
                "sku": product.sku,
                "requested_quantity": quantity,
                "available_quantity": available,
            })

    if short_items:
        raise InsufficientStockException(
            "Insufficient stock for order",
            short_items=short_items
        )

    order = SalesOrder.objects.create(
        order_number=_generate_order_number(),
        created_by_id=created_by_user_id,
        status=SalesOrderStatus.CONFIRMED,
        total_amount=0,
        warehouse_id=warehouse_id,
        **{k: v for k, v in data.items() if k != "warehouse"},
    )

    total_amount = 0
    order_items = []

    for item_data in items:
        product_id = item_data["product"]
        if hasattr(product_id, "id"):
            product_id = product_id.id

        product = Product.objects.get(id=product_id)
        quantity = item_data["quantity"]

        inventory = (
            Inventory.objects
            .select_for_update()
            .get(
                warehouse_id=warehouse_id,
                product=product,
            )
        )

        inventory.quantity_available = F("quantity_available") - quantity
        inventory.quantity_reserved = F("quantity_reserved") + quantity
        inventory.save(update_fields=["quantity_available", "quantity_reserved"])

        total_price = quantity * item_data["unit_price"]
        order_items.append(
            SalesOrderItem(
                sales_order=order,
                product=product,
                quantity=quantity,
                unit_price=item_data["unit_price"],
                total_price=total_price,
            )
        )
        total_amount += total_price

    SalesOrderItem.objects.bulk_create(order_items)
    order.total_amount = total_amount
    order.save(update_fields=["total_amount"])

    from .tasks import process_sales_order_created_event
    process_sales_order_created_event.delay(order.id)

    return order


def get_sales_order(so_id):
    try:
        return SalesOrder.objects.get(id=so_id)
    except SalesOrder.DoesNotExist:
        raise ResourceNotFoundException(
            "Sales order not found"
        )


@transaction.atomic
def dispatch_sales_order(so_id):
    """Dispatch sales order and create OUTBOUND transactions."""
    so = get_sales_order(so_id)

    if so.status != SalesOrderStatus.CONFIRMED:
        raise InvalidOperationException(
            "Order is not confirmed",
            code="ORDER_NOT_CONFIRMED"
        )

    warehouse_id = so.warehouse_id if hasattr(so, "warehouse_id") else (
        so.warehouse.id if hasattr(so, "warehouse") else None
    )

    for item in so.items.all():
        adjust_inventory(
            {
                "product_id": item.product.id,
                "warehouse_id": warehouse_id,
                "transaction_type": "OUTBOUND",
                "quantity": item.quantity,
                "notes": f"SO {so.order_number} dispatch",
            },
            performed_by_user_id=so.created_by_id
        )

        inventory = Inventory.objects.select_for_update().get(
            warehouse_id=warehouse_id,
            product=item.product,
        )
        inventory.quantity_reserved = F("quantity_reserved") - item.quantity
        inventory.save(update_fields=["quantity_reserved"])

    so.status = SalesOrderStatus.DISPATCHED
    so.dispatched_at = timezone.now()
    so.save()

    return so


@transaction.atomic
def deliver_sales_order(so_id):
    """Mark sales order as delivered."""
    so = get_sales_order(so_id)

    if so.status != SalesOrderStatus.DISPATCHED:
        raise InvalidOperationException(
            "Order is not dispatched",
            code="ORDER_NOT_DISPATCHED"
        )

    so.status = SalesOrderStatus.DELIVERED
    so.delivered_at = timezone.now()
    so.save()

    return so


@transaction.atomic
def cancel_sales_order(so_id, reason):
    """Cancel sales order and release reserved inventory."""
    so = get_sales_order(so_id)

    allowed_statuses = [
        SalesOrderStatus.PENDING,
        SalesOrderStatus.CONFIRMED,
    ]

    if so.status not in allowed_statuses:
        raise InvalidOperationException(
            "Order cannot be cancelled in current status",
            code="SO_CANCELLATION_NOT_ALLOWED"
        )

    warehouse_id = so.warehouse_id if hasattr(so, "warehouse_id") else (
        so.warehouse.id if hasattr(so, "warehouse") else None
    )

    for item in so.items.all():
        inventory = Inventory.objects.select_for_update().get(
            warehouse_id=warehouse_id,
            product=item.product,
        )
        inventory.quantity_available = F("quantity_available") + item.quantity
        inventory.quantity_reserved = F("quantity_reserved") - item.quantity
        inventory.save(update_fields=["quantity_available", "quantity_reserved"])

    so.status = SalesOrderStatus.CANCELLED
    so.notes = reason
    so.save()

    from .tasks import process_sales_order_cancelled_event
    process_sales_order_cancelled_event.delay(so.id)

    return so

        )

    so.status = (
        SalesOrderStatus.DELIVERED
    )

    so.delivered_at = (
        timezone.now()
    )

    so.save()

    return so