from rest_framework import serializers

from .models import (
    PurchaseOrder,
)


class PurchaseOrderSerializer(
    serializers.ModelSerializer
):
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
        )