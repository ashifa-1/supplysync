from rest_framework import serializers

from .models import (
    TransactionType,
)


class InventoryAdjustSerializer(
    serializers.Serializer
):
    product_id = serializers.IntegerField()

    warehouse_id = serializers.IntegerField()

    transaction_type = serializers.ChoiceField(
        choices=TransactionType.choices
    )

    quantity = serializers.IntegerField(
        min_value=1
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True
    )


class InventoryTransferSerializer(
    serializers.Serializer
):
    product_id = serializers.IntegerField()

    source_warehouse_id = (
        serializers.IntegerField()
    )

    destination_warehouse_id = (
        serializers.IntegerField()
    )

    quantity = serializers.IntegerField(
        min_value=1
    )

    notes = serializers.CharField(
        required=False,
        allow_blank=True
    )