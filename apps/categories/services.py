import random
import string

from apps.categories.models import Category
from core.exceptions import ResourceNotFoundException


def generate_category_code():
    while True:
        code = (
            "CAT-"
            + "".join(
                random.choices(
                    string.ascii_uppercase
                    + string.digits,
                    k=6,
                )
            )
        )

        if not Category.objects.filter(
            category_code=code
        ).exists():
            return code


def create_category(data: dict) -> Category:
    parent_category = None
    parent_category_id = data.pop("parent_category_id", None)

    if parent_category_id is not None:
        try:
            parent_category = Category.objects.get(
                id=parent_category_id
            )
        except Category.DoesNotExist:
            raise ResourceNotFoundException(
                "Parent category not found"
            )

    if not data.get("category_code"):
        data["category_code"] = generate_category_code()

    return Category.objects.create(
        parent_category=parent_category,
        **data,
    )


def get_category_tree() -> list:
    return list(
        Category.objects.filter(
            parent_category__isnull=True,
        ).prefetch_related("children")
    )
