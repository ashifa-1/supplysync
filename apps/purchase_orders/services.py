import datetime

from django.db import transaction
from django.utils import timezone
from django.core.cache import cache

from .models import (
    PurchaseOrder,
    PurchaseOrderItem,
    PurchaseOrderStatus,
)

from apps.products.models import Product
from apps.inventory.services import adjust_inventory
from core.exceptions import (
    ResourceNotFoundException,
    InvalidOperationException,
)


def generate_po_number():
    today = datetime.date.today().strftime("%Y%m%d")
    redis_key = f"po-sequence:{today}"
    
    sequence = cache.incr(redis_key)
    
    if sequence == 1:
        cache.expire(redis_key, 86400)
    
    return f"PO-{today}-{sequence:04d}"


@transaction.atomic
def create_purchase_order(
    data,
    created_by_user_id
):
    items = data.pop("items", [])
    data["po_number"] = generate_po_number()
    data["created_by_id"] = created_by_user_id
    data["status"] = PurchaseOrderStatus.DRAFT

    purchase_order = PurchaseOrder.objects.create(**data)

    total_amount = 0
    purchase_items = []

    for item_data in items:
        product_id = item_data["product"]
        if hasattr(product_id, "id"):
            product_id = product_id.id

        product = Product.objects.get(id=product_id)
        quantity_ordered = item_data["quantity_ordered"]
        unit_price = item_data["unit_price"]
        total_price = quantity_ordered * unit_price

        purchase_items.append(
            PurchaseOrderItem(
                purchase_order=purchase_order,
                product=product,
                quantity_ordered=quantity_ordered,
                quantity_received=item_data.get("quantity_received", 0),
                unit_price=unit_price,
                total_price=total_price,
            )
        )
        total_amount += total_price

    PurchaseOrderItem.objects.bulk_create(purchase_items)
    purchase_order.total_amount = total_amount
    purchase_order.save(update_fields=["total_amount"])

    return purchase_order


def get_purchase_order(po_id):
    try:
        return PurchaseOrder.objects.get(id=po_id)
    except PurchaseOrder.DoesNotExist:
        raise ResourceNotFoundException(
            "Purchase order not found"
        )


def submit_purchase_order(po_id):
    """
    Move PO from DRAFT to PENDING_APPROVAL.
    """
    po = get_purchase_order(po_id)

    if po.status != PurchaseOrderStatus.DRAFT:
        raise InvalidOperationException(
            "Purchase order is not in DRAFT status",
            code="INVALID_PO_STATUS"
        )

    if not po.items.exists():
        raise InvalidOperationException(
            "Purchase order has no items",
            code="PO_HAS_NO_ITEMS"
        )

    po.status = PurchaseOrderStatus.PENDING_APPROVAL
    po.save(update_fields=["status"])

    return po


def approve_purchase_order(po_id, approved_by_user_id):
    """Approve purchase order."""
    po = get_purchase_order(po_id)

    if po.status != PurchaseOrderStatus.PENDING_APPROVAL:
        raise InvalidOperationException(
            "Purchase order is not pending approval",
            code="PO_NOT_PENDING_APPROVAL"
        )

    if po.created_by_id == approved_by_user_id:
        raise InvalidOperationException(
            "Cannot approve own purchase order",
            code="SELF_APPROVAL_NOT_ALLOWED"
        )

    po.status = PurchaseOrderStatus.APPROVED
    po.approved_by_id = approved_by_user_id
    po.approved_at = timezone.now()
    po.save()

    return po


@transaction.atomic
def receive_purchase_order(po_id, data, performed_by_user_id):
    """Record receipt of goods for purchase order."""
    po = get_purchase_order(po_id)
    
    items_data = data.get("items", [])
    actual_delivery_date = data.get("actual_delivery_date")
    
    all_fully_received = True
    
    for item_data in items_data:
        po_item_id = item_data.get("po_item_id")
        quantity_received = item_data.get("quantity_received", 0)
        
        try:
            po_item = PurchaseOrderItem.objects.get(
                id=po_item_id,
                purchase_order=po
            )
        except PurchaseOrderItem.DoesNotExist:
            raise ResourceNotFoundException(
                "Purchase order item not found"
            )
        
        already_received = po_item.quantity_received
        remaining_to_receive = po_item.quantity_ordered - already_received
        
        if quantity_received > remaining_to_receive:
            raise InvalidOperationException(
                "Quantity received exceeds quantity ordered",
                code="INVALID_RECEIPT_QUANTITY"
            )
        
        if quantity_received > 0:
            adjust_inventory(
                {
                    "product_id": po_item.product.id,
                    "warehouse_id": po.warehouse.id if hasattr(po, 'warehouse') else None,
                    "transaction_type": "INBOUND",
                    "quantity": quantity_received,
                    "notes": f"PO {po.po_number} receipt",
                },
                performed_by_user_id
            )
            
            po_item.quantity_received += quantity_received
            po_item.save(update_fields=["quantity_received"])
        
        if po_item.quantity_received < po_item.quantity_ordered:
            all_fully_received = False
    
    if actual_delivery_date:
        po.actual_delivery_date = actual_delivery_date
    
    if all_fully_received:
        po.status = PurchaseOrderStatus.RECEIVED
    else:
        po.status = PurchaseOrderStatus.PARTIALLY_RECEIVED
    
    po.save()
    
    from .tasks import process_purchase_order_received_event
    process_purchase_order_received_event.delay(po.id)
    
    return po


def cancel_purchase_order(po_id, reason):
    """Cancel purchase order."""
    po = get_purchase_order(po_id)

    allowed_statuses = [
        PurchaseOrderStatus.DRAFT,
        PurchaseOrderStatus.PENDING_APPROVAL,
        PurchaseOrderStatus.APPROVED,
    ]

    if po.status not in allowed_statuses:
        raise InvalidOperationException(
            "Purchase order cannot be cancelled in current status",
            code="PO_CANCELLATION_NOT_ALLOWED"
        )

    po.status = PurchaseOrderStatus.CANCELLED
    po.notes = reason
    po.save()

    return po