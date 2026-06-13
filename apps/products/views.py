from rest_framework import generics
from rest_framework.response import Response
from rest_framework import status

from rest_framework.permissions import (
    IsAuthenticated
)

from core.permissions import (
    IsWarehouseManagerOrAdmin
)

from .models import Product
from .serializers import (
    ProductSerializer,
)
from .services import (
    create_product,
    get_product_with_inventory,
)
from .filters import ProductFilter


class ProductListCreateView(
    generics.ListCreateAPIView
):
    serializer_class = (
        ProductSerializer
    )

    filterset_class = (
        ProductFilter
    )

    queryset = (
        Product.objects.all()
    )

    def get_permissions(self):
        if self.request.method == "POST":
            return [
                IsWarehouseManagerOrAdmin()
            ]

        return [
            IsAuthenticated()
        ]

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

        product = (
            create_product(
                serializer.validated_data
            )
        )

        return Response(
            ProductSerializer(
                product
            ).data,
            status=status.HTTP_201_CREATED,
        )


class ProductDetailView(
    generics.RetrieveAPIView
):
    permission_classes = [
        IsAuthenticated
    ]
    def retrieve(
        self,
        request,
        *args,
        **kwargs
    ):
        data = (
            get_product_with_inventory(
                self.kwargs["pk"]
            )
        )

        return Response(data)