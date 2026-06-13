from rest_framework import serializers

from .models import Product

from core.exceptions import (
    InvalidOperationException,
)


class ProductSerializer(
    serializers.ModelSerializer
):
    sku = serializers.CharField(
        required=False
    )

    def validate(
        self,
        attrs
    ):
        if (
            self.instance
            and "sku" in attrs
        ):
            raise (
                InvalidOperationException(
                    "SKU_IMMUTABLE"
                )
            )

        return attrs

    class Meta:
        model = Product
        fields = "__all__"

        read_only_fields = (
            "id",
            "created_at",
            "updated_at",
            "is_deleted",
        )