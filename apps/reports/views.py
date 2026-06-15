from rest_framework.views import APIView
from rest_framework.response import Response

from .services import (
    get_inventory_summary,
    get_purchase_order_report,
    get_sales_order_report,
)


class InventoryReportView(APIView):
    def get(self, request):
        return Response(get_inventory_summary())


class PurchaseOrderReportView(APIView):
    def get(self, request):
        return Response(get_purchase_order_report())


class SalesOrderReportView(APIView):
    def get(self, request):
        return Response(get_sales_order_report())
