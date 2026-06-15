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
    """
    Create purchase order in DRAFT state.
    """

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
    """
    Return purchase order by id.
    """

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
    """
    Move PO from DRAFT
    to PENDING_APPROVAL.
    """

    po = get_purchase_order(
        po_id
    )

    if (
        po.status
        != PurchaseOrderStatus.DRAFT
    ):
        raise InvalidOperationException(
            "INVALID_PO_STATUS"
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
    """
    Approve purchase order.
    """

    po = get_purchase_order(
        po_id
    )

    if (
        po.status
        != PurchaseOrderStatus
        .PENDING_APPROVAL
    ):
        raise InvalidOperationException(
            "PO_NOT_PENDING_APPROVAL"
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


def cancel_purchase_order(
    po_id,
    reason
):
    """
    Cancel purchase order.
    """

    po = get_purchase_order(
        po_id
    )

    allowed_statuses = [
        PurchaseOrderStatus.DRAFT,
        PurchaseOrderStatus.PENDING_APPROVAL,
        PurchaseOrderStatus.APPROVED,
    ]

    if (
        po.status
        not in allowed_statuses
    ):
        raise InvalidOperationException(
            "PO_CANCELLATION_NOT_ALLOWED"
        )

    po.status = (
        PurchaseOrderStatus.CANCELLED
    )

    po.notes = reason

    po.save()

    return po