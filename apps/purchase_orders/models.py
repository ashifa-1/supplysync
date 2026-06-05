from django.conf import settings
from django.db import models

from apps.products.models import Product

from core.models import BaseModel
from apps.suppliers.models import Supplier
from apps.warehouses.models import Warehouse

class PurchaseOrderStatus(models.TextChoices):
    DRAFT = "DRAFT", "Draft"
    SUBMITTED = "SUBMITTED", "Submitted"
    APPROVED = "APPROVED", "Approved"
    PARTIALLY_RECEIVED = (
        "PARTIALLY_RECEIVED",
        "Partially Received"
    )
    RECEIVED = "RECEIVED", "Received"
    CANCELLED = "CANCELLED", "Cancelled"

class PurchaseOrder(BaseModel):
    po_number = models.CharField(
        max_length=50,
        unique=True
    )

    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT
    )

    warehouse = models.ForeignKey(
        Warehouse,
        on_delete=models.PROTECT
    )

    status = models.CharField(
        max_length=30,
        choices=PurchaseOrderStatus.choices,
        default=PurchaseOrderStatus.DRAFT
    )

    expected_delivery_date = models.DateField(
        null=True,
        blank=True
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name="approved_purchase_orders"
    )

    approved_at = models.DateTimeField(
        null=True,
        blank=True
    )

    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=0
    )

    notes = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = "purchase_orders"

    def __str__(self):
        return self.po_number
    

class PurchaseOrderItem(BaseModel):
    purchase_order = models.ForeignKey(
        PurchaseOrder,
        on_delete=models.CASCADE,
        related_name="items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.PROTECT
    )

    quantity_ordered = models.IntegerField()

    quantity_received = models.IntegerField(
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
        db_table = "purchase_order_items"

    def __str__(self):
        return (
            f"{self.purchase_order.po_number} - "
            f"{self.product.name}"
        )