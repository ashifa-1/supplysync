from django.db.models import Count, Sum, F

from apps.inventory.models import Inventory
from apps.purchase_orders.models import PurchaseOrder
from apps.sales_orders.models import SalesOrder


def get_inventory_summary():
    total_warehouses = Inventory.objects.values("warehouse").distinct().count()
    total_products = Inventory.objects.values("product").distinct().count()
    low_stock_count = Inventory.objects.filter(
        quantity_available__lte=F("product__reorder_level")
    ).count()
    total_quantity_available = Inventory.objects.aggregate(
        total=Sum("quantity_available"))[
        "total"] or 0

    return {
        "total_warehouses": total_warehouses,
        "total_products": total_products,
        "low_stock_count": low_stock_count,
        "total_quantity_available": total_quantity_available,
    }


def get_purchase_order_report():
    return list(
        PurchaseOrder.objects.values("status").annotate(
            count=Count("id"),
            total_amount=Sum("total_amount"),
        )
    )


def get_sales_order_report():
    return list(
        SalesOrder.objects.values("status").annotate(
            count=Count("id"),
            total_amount=Sum("total_amount"),
        )
    )
