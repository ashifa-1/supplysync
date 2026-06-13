import datetime

from django.utils import timezone

from .models import (
    PurchaseOrder,
    PurchaseOrderStatus,
)

from core.exceptions import (
    ResourceNotFoundException,
    InvalidOperationException,
)


def generate_po_number():
    today = (
        datetime.date.today()
        .strftime("%Y%m%d")
    )

    count = (
        PurchaseOrder.objects.filter(
            created_at__date=
            datetime.date.today()
        ).count()
        + 1
    )

    return (
        f"PO-{today}-{count:04d}"
    )


def create_purchase_order(
    data,
    created_by_user_id
):
    data["po_number"] = (
        generate_po_number()
    )

    data["created_by_id"] = (
        created_by_user_id
    )

    data["status"] = (
        PurchaseOrderStatus.DRAFT
    )

    return PurchaseOrder.objects.create(
        **data
    )


def get_purchase_order(
    po_id
):
    try:
        return PurchaseOrder.objects.get(
            id=po_id
        )
    except PurchaseOrder.DoesNotExist:
        raise ResourceNotFoundException(
            "Purchase order not found"
        )


def submit_purchase_order(
    po_id
):
    po = get_purchase_order(
        po_id
    )

    if (
        not po.items.exists()
    ):
        raise InvalidOperationException(
            "PO_HAS_NO_ITEMS"
        )

    po.status = (
        PurchaseOrderStatus
        .PENDING_APPROVAL
    )

    po.save(
        update_fields=["status"]
    )

    return po


def approve_purchase_order(
    po_id,
    approved_by_user_id
):
    po = get_purchase_order(
        po_id
    )

    if (
        po.created_by_id
        ==
        approved_by_user_id
    ):
        raise InvalidOperationException(
            "SELF_APPROVAL_NOT_ALLOWED"
        )

    po.status = (
        PurchaseOrderStatus.APPROVED
    )

    po.approved_by_id = (
        approved_by_user_id
    )

    po.approved_at = (
        timezone.now()
    )

    po.save()

    return po