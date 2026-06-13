from django.urls import path

from .views import (
    PurchaseOrderListCreateView,
    PurchaseOrderSubmitView,
    PurchaseOrderApproveView,
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
]