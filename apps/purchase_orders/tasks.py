import logging

from celery import shared_task

logger = logging.getLogger(__name__)


@shared_task
def process_purchase_order_received_event(po_id):
    """Process purchase order received event."""
    logger.info(
        "Processed purchase order received event: PO %s",
        po_id,
    )
    return True


@shared_task
def process_sales_order_created_event(so_id):
    """Process sales order created event."""
    logger.info(
        "Processed sales order created event: SO %s",
        so_id,
    )
    return True


@shared_task
def process_sales_order_cancelled_event(so_id):
    """Process sales order cancelled event."""
    logger.info(
        "Processed sales order cancelled event: SO %s",
        so_id,
    )
    return True
