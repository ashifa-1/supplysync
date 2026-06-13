from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .serializers import (
    InventoryAdjustSerializer,
)

from rest_framework import generics

from .models import Inventory

from .services import (
    get_low_stock_alerts,
    get_warehouse_inventory,
)

from .serializers import (
    InventoryTransferSerializer,
)

from .services import (
    transfer_inventory,
)

from .services import (
    adjust_inventory,
)


class InventoryAdjustView(
    APIView
):
    def post(
        self,
        request
    ):
        serializer = (
            InventoryAdjustSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        inventory_transaction = (
            adjust_inventory(
                serializer.validated_data,
                request.user.id,
            )
        )

        return Response(
            {
                "id":
                    inventory_transaction.id,
                "message":
                    "Inventory adjusted successfully.",
            },
            status=status.HTTP_200_OK,
        )
    

class InventoryTransferView(
    APIView
):
    def post(
        self,
        request
    ):
        serializer = (
            InventoryTransferSerializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        result = (
            transfer_inventory(
                serializer.validated_data,
                request.user.id,
            )
        )

        return Response(
            result,
            status=status.HTTP_200_OK,
        )



class LowStockAlertView(
    APIView
):
    def get(
        self,
        request
    ):
        return Response(
            get_low_stock_alerts()
        )
    

class WarehouseInventoryView(
    generics.ListAPIView
):
    serializer_class = None

    def list(
        self,
        request,
        *args,
        **kwargs
    ):
        inventory = (
            get_warehouse_inventory(
                self.kwargs[
                    "warehouse_id"
                ]
            )
        )

        results = []

        for item in inventory:
            results.append(
                {
                    "product_id":
                        item.product.id,
                    "sku":
                        item.product.sku,
                    "product_name":
                        item.product.name,
                    "quantity_available":
                        item.quantity_available,
                    "quantity_reserved":
                        item.quantity_reserved,
                    "quantity_damaged":
                        item.quantity_damaged,
                }
            )

        return Response(results)