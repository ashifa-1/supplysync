from django.urls import path

from .views import (
    InventoryReportView,
    PurchaseOrderReportView,
    SalesOrderReportView,
)

urlpatterns = [
    path(
        "inventory/",
        InventoryReportView.as_view(),
        name="inventory-report",
    ),
    path(
        "purchase-orders/",
        PurchaseOrderReportView.as_view(),
        name="po-report",
    ),
    path(
        "sales-orders/",
        SalesOrderReportView.as_view(),
        name="so-report",
    ),
]
