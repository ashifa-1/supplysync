from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from .models import PurchaseOrder

from .serializers import (
    PurchaseOrderSerializer,
)

from .services import (
    create_purchase_order,
    submit_purchase_order,
    approve_purchase_order,
    cancel_purchase_order,
    receive_purchase_order,
)


class PurchaseOrderListCreateView(
    generics.ListCreateAPIView
):
    queryset = (
        PurchaseOrder.objects.all()
    )

    serializer_class = (
        PurchaseOrderSerializer
    )

    def create(
        self,
        request,
        *args,
        **kwargs
    ):
        serializer = (
            self.get_serializer(
                data=request.data
            )
        )

        serializer.is_valid(
            raise_exception=True
        )

        po = (
            create_purchase_order(
                serializer.validated_data,
                request.user.id,
            )
        )

        return Response(
            PurchaseOrderSerializer(
                po
            ).data,
            status=status.HTTP_201_CREATED,
        )


class PurchaseOrderSubmitView(
    APIView
):
    def post(
        self,
        request,
        pk
    ):
        po = submit_purchase_order(
            pk
        )

        return Response(
            {
                "id": po.id,
                "status": po.status,
            }
        )


class PurchaseOrderCancelView(
    APIView
):
    def post(
        self,
        request,
        pk
    ):
        po = cancel_purchase_order(
            pk,
            request.data.get(
                "reason",
                "Order cancelled by user",
            ),
        )

        return Response(
            {
                "id": po.id,
                "status": po.status,
                "notes": po.notes,
            }
        )


class PurchaseOrderApproveView(
    APIView
):
    def post(
        self,
        request,
        pk
    ):
        po = approve_purchase_order(
            pk,
            request.user.id,
        )

        return Response(
            {
                "id": po.id,
                "status": po.status,
            }
        )


class PurchaseOrderReceiveView(
    APIView
):
    def post(
        self,
        request,
        pk
    ):
        po = receive_purchase_order(
            pk,
            request.data,
            request.user.id,
        )

        return Response(
            PurchaseOrderSerializer(
                po
            ).data,
            status=status.HTTP_200_OK,
        )