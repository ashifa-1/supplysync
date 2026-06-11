from rest_framework import serializers

from .models import Warehouse
from core.exceptions import (
    InvalidOperationException
)

class WarehouseSerializer( serializers.ModelSerializer):

    warehouse_code = serializers.CharField(
        required=False
    )

    def validate(self, attrs):
        if (
            self.instance
            and "warehouse_code" in attrs
        ):
            raise InvalidOperationException(
                "WAREHOUSE_CODE_IMMUTABLE"
            )

        return attrs

    class Meta:
        model = Warehouse
        fields = "__all__"
        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_deleted",
        )
