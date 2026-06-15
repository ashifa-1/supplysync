from django.urls import path

from .views import (
    PurchaseOrderListCreateView,
    PurchaseOrderSubmitView,
    PurchaseOrderApproveView,
    PurchaseOrderCancelView,
    PurchaseOrderReceiveView,
)

urlpatterns = [
    path(
        "",
        PurchaseOrderListCreateView.as_view(),
        name="po-list",
    ),

    path(
        "<int:pk>/submit/",
        PurchaseOrderSubmitView.as_view(),
        name="po-submit",
    ),

    path(
        "<int:pk>/approve/",
        PurchaseOrderApproveView.as_view(),
        name="po-approve",
    ),
    path(
        "<int:pk>/cancel/",
        PurchaseOrderCancelView.as_view(),
        name="po-cancel",
    ),
    path(
        "<int:pk>/receive/",
        PurchaseOrderReceiveView.as_view(),
        name="po-receive",
    ),
]