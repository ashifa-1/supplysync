from rest_framework import serializers

from .models import SalesOrder


class SalesOrderSerializer(
    serializers.ModelSerializer
):
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
        )