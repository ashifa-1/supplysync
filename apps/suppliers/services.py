import random
import string

from .models import Supplier

from core.exceptions import (
    ResourceNotFoundException,
)


def generate_supplier_code():
    while True:
        code = (
            "SUP-"
            + "".join(
                random.choices(
                    string.ascii_uppercase
                    + string.digits,
                    k=6
                )
            )
        )

        if not Supplier.objects.filter(
            supplier_code=code
        ).exists():
            return code


def create_supplier(
    data: dict
):
    if not data.get(
        "supplier_code"
    ):
        data[
            "supplier_code"
        ] = generate_supplier_code()

    return Supplier.objects.create(
        **data
    )


def get_supplier_by_id(
    supplier_id: int
):
    try:
        return Supplier.objects.get(
            id=supplier_id
        )
    except Supplier.DoesNotExist:
        raise ResourceNotFoundException(
            "Supplier not found"
        )


def update_supplier(
    supplier_id: int,
    data: dict
):
    supplier = get_supplier_by_id(
        supplier_id
    )

    for key, value in data.items():
        setattr(
            supplier,
            key,
            value
        )

    supplier.save()

    return supplier


def list_suppliers(
    filters: dict,
    page: int,
    page_size: int
):
    return Supplier.objects.all()


def delete_supplier(
    supplier_id: int
):
    supplier = get_supplier_by_id(
        supplier_id
    )

    supplier.delete()