from rest_framework import serializers

from .models import Category


class CategorySerializer(
    serializers.ModelSerializer
):
    category_code = serializers.CharField(
        required=False
    )

    class Meta:
        model = Category
        fields = "__all__"



class CategoryTreeSerializer(
    serializers.ModelSerializer
):
    children = serializers.SerializerMethodField()

    class Meta:
        model = Category
        fields = (
            "id",
            "category_code",
            "name",
            "children",
        )

    def get_children(
        self,
        obj
    ):
        return (
            CategoryTreeSerializer(
                obj.children.all(),
                many=True,
            ).data
        )