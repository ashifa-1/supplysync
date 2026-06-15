from rest_framework import serializers

from apps.products.models import Product
from .models import (
    PurchaseOrder,
    PurchaseOrderItem,
)


class PurchaseOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    class Meta:
        model = PurchaseOrderItem
        fields = (
            "product",
            "quantity_ordered",
            "quantity_received",
            "unit_price",
            "total_price",
        )
        read_only_fields = (
            "quantity_received",
            "total_price",
        )


class PurchaseOrderSerializer(serializers.ModelSerializer):
    items = PurchaseOrderItemSerializer(many=True)

    class Meta:
        model = PurchaseOrder
        fields = "__all__"
        read_only_fields = (
            "id",
            "po_number",
            "status",
            "created_by",
            "approved_by",
            "approved_at",
            "created_at",
            "updated_at",
            "is_deleted",
            "total_amount",
        )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "Purchase order must contain at least one item."
            )
        return value