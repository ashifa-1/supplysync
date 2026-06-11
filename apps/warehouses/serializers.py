from rest_framework import serializers

from .models import Warehouse


class WarehouseSerializer( serializers.ModelSerializer):

    warehouse_code = serializers.CharField(
        required=False
    )
    class Meta:
        model = Warehouse
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_deleted",
        )