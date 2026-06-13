from django.urls import path

from .views import (
    SalesOrderListCreateView,
    SalesOrderDispatchView,
    SalesOrderDeliverView,
)

urlpatterns = [
    path(
        "",
        SalesOrderListCreateView.as_view(),
        name="sales-order-list",
    ),

    path(
        "<int:pk>/dispatch/",
        SalesOrderDispatchView.as_view(),
        name="sales-order-dispatch",
    ),

    path(
        "<int:pk>/deliver/",
        SalesOrderDeliverView.as_view(),
        name="sales-order-deliver",
    ),
]