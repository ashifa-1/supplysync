from django.conf import settings
from django.db import models

from apps.products.models import Product

from core.models import BaseModel
from apps.warehouses.models import Warehouse

class SalesOrderStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    CONFIRMED = "CONFIRMED", "Confirmed"
    PICKED = "PICKED", "Picked"
    SHIPPED = "SHIPPED", "Shipped"
    DELIVERED = "DELIVERED", "Delivered"
    CANCELLED = "CANCELLED", "Cancelled"

class SalesOrder(BaseModel):
    order_number = models.CharField(
        max_length=50,
        unique=True
    )

    customer_name = models.CharField(
        max_length=200
    )

    customer_email = models.EmailField(
        null=True,
        blank=True
    )

    customer_phone = models.CharField(
        max_length=20,
        null=True,
        blank=True
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=30,
        choices=SalesOrderStatus.choices,
        default=SalesOrderStatus.DRAFT
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    confirmed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="confirmed_sales_orders"
    )

    confirmed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    notes = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "sales_orders"

    def __str__(self):
        return self.order_number
    

class SalesOrderItem(BaseModel):
    sales_order = models.ForeignKey(
        SalesOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity_ordered = models.IntegerField()

    quantity_shipped = models.IntegerField(
        default=0
    )

    unit_price = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    total_price = models.DecimalField(
        max_digits=15,
        decimal_places=2
    )

    class Meta:
        db_table = "sales_order_items"

    def __str__(self):
        return (
            f"{self.sales_order.order_number} - "
            f"{self.product.name}"
        )