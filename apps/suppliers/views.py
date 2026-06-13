from rest_framework import generics

from .models import Supplier
from .serializers import (
    SupplierSerializer,
)
from .services import (
    create_supplier,
    update_supplier,
    get_supplier_by_id,
    delete_supplier,
)


class SupplierListCreateView(
    generics.ListCreateAPIView
):
    queryset = (
        Supplier.objects.all()
    )

    serializer_class = (
        SupplierSerializer
    )

    def perform_create(
        self,
        serializer
    ):
        create_supplier(
            serializer.validated_data
        )


class SupplierDetailView(
    generics.RetrieveUpdateDestroyAPIView
):
    serializer_class = (
        SupplierSerializer
    )

    def get_object(
        self
    ):
        return get_supplier_by_id(
            self.kwargs["pk"]
        )

    def perform_update(
        self,
        serializer
    ):
        update_supplier(
            self.kwargs["pk"],
            serializer.validated_data,
        )

    def perform_destroy(
        self,
        instance
    ):
        delete_supplier(
            instance.id
        )