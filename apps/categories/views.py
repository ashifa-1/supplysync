from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .models import Category
from .serializers import (
    CategorySerializer,
    CategoryTreeSerializer,
)
from .services import (
    create_category,
    get_category_tree,
)

class CategoryListCreateView(
    generics.ListCreateAPIView
):
    queryset = (
        Category.objects.all()
    )

    serializer_class = (
        CategorySerializer
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

        category = (
            create_category(
                serializer.validated_data
            )
        )

        return Response(
            CategorySerializer(
                category
            ).data,
            status=status.HTTP_201_CREATED,
        )


class CategoryTreeView(
    APIView
):
    def get(
        self,
        request
    ):
        categories = (
            get_category_tree()
        )

        return Response(
            CategoryTreeSerializer(
                categories,
                many=True,
            ).data
        )