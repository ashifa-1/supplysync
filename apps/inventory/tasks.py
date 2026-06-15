import logging

from celery import shared_task
from django.core.cache import cache

from .models import InventoryTransaction
from core.constants import INVENTORY_LOW_STOCK_KEY

logger = logging.getLogger(__name__)


@shared_task
def process_inventory_updated_event(
    transaction_id
):
    try:
        transaction = InventoryTransaction.objects.select_related(
            "product", "warehouse", "performed_by"
        ).get(id=transaction_id)
    except InventoryTransaction.DoesNotExist:
        logger.warning(
            "Inventory updated event skipped: transaction %s not found",
            transaction_id,
        )
        return False

    logger.info(
        "Processed inventory updated event: %s %s %s %s",
        transaction.id,
        transaction.transaction_type,
        transaction.quantity,
        transaction.product.sku,
    )

    return True


@shared_task
def process_inventory_transfer_event(
    reference_id
):
    transactions = InventoryTransaction.objects.filter(
        reference_id=reference_id
    )

    if not transactions.exists():
        logger.warning(
            "Inventory transfer event skipped: reference %s not found",
            reference_id,
        )
        return False

    logger.info(
        "Processed inventory transfer event: %s with %s transactions",
        reference_id,
        transactions.count(),
    )

    return True


@shared_task
def auto_invalidate_low_stock_cache():
    cache.delete(INVENTORY_LOW_STOCK_KEY)
    logger.info("Auto invalidated low stock cache")
    return True