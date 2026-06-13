import uuid

from django.utils import timezone

from .models import (
    SalesOrder,
    SalesOrderStatus,
)

from core.exceptions import (
    ResourceNotFoundException,
    InvalidOperationException,
)


def create_sales_order(
    data,
    created_by_user_id
):
    data["order_number"] = (
        "SO-"
        + str(uuid.uuid4())[:8]
    )

    data["created_by_id"] = (
        created_by_user_id
    )

    data["status"] = (
        SalesOrderStatus.CONFIRMED
    )

    return SalesOrder.objects.create(
        **data
    )


def get_sales_order(
    so_id
):
    try:
        return SalesOrder.objects.get(
            id=so_id
        )
    except SalesOrder.DoesNotExist:
        raise ResourceNotFoundException(
            "Sales order not found"
        )


def dispatch_sales_order(
    so_id
):
    so = get_sales_order(
        so_id
    )

    so.status = (
        SalesOrderStatus.DISPATCHED
    )

    so.dispatched_at = (
        timezone.now()
    )

    so.save()

    return so


def deliver_sales_order(
    so_id
):
    so = get_sales_order(
        so_id
    )

    if (
        so.status
        !=
        SalesOrderStatus.DISPATCHED
    ):
        raise (
            InvalidOperationException(
                "ORDER_NOT_DISPATCHED"
            )
        )

    so.status = (
        SalesOrderStatus.DELIVERED
    )

    so.delivered_at = (
        timezone.now()
    )

    so.save()

    return so