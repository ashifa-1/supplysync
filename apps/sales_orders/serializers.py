from rest_framework import serializers

from apps.products.models import Product
from .models import SalesOrder, SalesOrderItem


class SalesOrderItemSerializer(serializers.ModelSerializer):
    product = serializers.PrimaryKeyRelatedField(
        queryset=Product.objects.all()
    )

    class Meta:
        model = SalesOrderItem
        fields = (
            "product",
            "quantity",
            "unit_price",
            "total_price",
        )
        read_only_fields = (
            "total_price",
        )


class SalesOrderSerializer(serializers.ModelSerializer):
    items = SalesOrderItemSerializer(many=True)

    class Meta:
        model = SalesOrder
        fields = "__all__"
        read_only_fields = (
            "id",
            "order_number",
            "status",
            "created_by",
            "dispatched_at",
            "delivered_at",
            "created_at",
            "updated_at",
            "is_deleted",
            "total_amount",
        )

    def validate_items(self, value):
        if not value:
            raise serializers.ValidationError(
                "Sales order must contain at least one item."
            )
        return value