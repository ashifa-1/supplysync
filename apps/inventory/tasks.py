from celery import shared_task


@shared_task
def process_inventory_updated_event(
    transaction_id
):
    return True


@shared_task
def process_inventory_transfer_event(
    reference_id
):
    return True