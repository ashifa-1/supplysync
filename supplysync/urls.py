from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path("admin/", admin.site.urls),

    path(
        "api/v1/auth/",
        include("apps.accounts.urls")
    ),
    path(
        "api/v1/warehouses/",
        include(
            "apps.warehouses.urls"
        ),
    ),
    path(
        "api/v1/categories/",
        include(
            "apps.categories.urls"
        ),
    ),
    path(
        "api/v1/products/",
        include(
            "apps.products.urls"
        ),
    ),
    path(
        "api/v1/inventory/",
        include(
            "apps.inventory.urls"
        ),
    ),
    path(
        "api/v1/suppliers/",
        include(
            "apps.suppliers.urls"
        ),
    ),
    path(
        "api/v1/purchase-orders/",
        include(
            "apps.purchase_orders.urls"
        ),
    ),
    path(
        "api/v1/sales-orders/",
        include(
            "apps.sales_orders.urls"
        ),
    ),
    path(
        "api/v1/reports/",
        include(
            "apps.reports.urls"
        ),
    ),
]   