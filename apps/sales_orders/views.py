from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework import generics

from .models import SalesOrder

from .serializers import (
    SalesOrderSerializer,
)

from .services import (
    create_sales_order,
    dispatch_sales_order,
    deliver_sales_order,
    cancel_sales_order,
)


class SalesOrderListCreateView(
    generics.ListCreateAPIView
):
    queryset = (
        SalesOrder.objects.all()
    )

    serializer_class = (
        SalesOrderSerializer
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

        so = (
            create_sales_order(
                serializer.validated_data,
                request.user.id,
            )
        )

        return Response(
            SalesOrderSerializer(
                so
            ).data,
            status=status.HTTP_201_CREATED,
        )


class SalesOrderDispatchView(
    APIView
):
    def post(
        self,
        request,
        pk
    ):
        so = dispatch_sales_order(
            pk
        )

        return Response(
            {
                "id": so.id,
                "status": so.status,
            }
        )


class SalesOrderDeliverView(
    APIView
):
    def post(
        self,
        request,
        pk
    ):
        so = deliver_sales_order(
            pk
        )

        return Response(
            {
                "id": so.id,
                "status": so.status,
            }
        )


class SalesOrderCancelView(
    APIView
):
    def post(
        self,
        request,
        pk
    ):
        so = cancel_sales_order(
            pk,
            request.data.get(
                "reason",
                "Order cancelled by user",
            ),
        )

        return Response(
            SalesOrderSerializer(
                so
            ).data,
            status=status.HTTP_200_OK,
        )