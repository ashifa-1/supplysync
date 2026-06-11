import random
import string

from .models import Category


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


def create_category(data):
    if not data.get(
        "category_code"
    ):
        data[
            "category_code"
        ] = generate_category_code()

    return Category.objects.create(
        **data
    )


def get_category_tree():
    return Category.objects.filter(
        parent_category__isnull=True
    )