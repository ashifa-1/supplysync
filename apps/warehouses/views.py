from rest_framework import generics
from rest_framework.permissions import (
    IsAuthenticated
)
from rest_framework.response import Response
from rest_framework import status

from .models import Warehouse
from .serializers import (
    WarehouseSerializer,
)
from .services import (
    get_warehouse_by_id,
    create_warehouse,
    get_warehouse_with_summary,
)

from core.permissions import (
    IsAdminUser,
)


class WarehouseListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = (
        WarehouseSerializer
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

        warehouse = (
            create_warehouse(
                serializer.validated_data
            )
        )

        return Response(
            WarehouseSerializer(
                warehouse
            ).data,
            status=status.HTTP_201_CREATED
        )

    def get_queryset(self):
        queryset = (
            Warehouse.objects.all()
        )

        city = self.request.GET.get(
            "city"
        )

        state = self.request.GET.get(
            "state"
        )

        if city:
            queryset = (
                queryset.filter(
                    city=city
                )
            )

        if state:
            queryset = (
                queryset.filter(
                    state=state
                )
            )

        return queryset

    def get_permissions(
        self
    ):
        if (
            self.request.method
            == "POST"
        ):
            return [
                IsAdminUser()
            ]

        return [
            IsAuthenticated()
        ]


class WarehouseDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = (
        WarehouseSerializer
    )

    def get_permissions(
        self
    ):
        if self.request.method in [
            "PATCH",
            "PUT",
            "DELETE",
        ]:
            return [
                IsAdminUser()
            ]

        return [
            IsAuthenticated()
        ]

    def get_object(
        self
    ):
        return get_warehouse_by_id(
            self.kwargs["pk"]
        )

    def retrieve(
        self,
        request,
        *args,
        **kwargs
    ):
        data = (
            get_warehouse_with_summary(
                self.kwargs["pk"]
            )
        )

        return Response(
            data
        )

    def destroy(
        self,
        request,
        *args,
        **kwargs
    ):
        warehouse = (
            self.get_object()
        )

        warehouse.delete()

        return Response(
            status=status.HTTP_204_NO_CONTENT
        )