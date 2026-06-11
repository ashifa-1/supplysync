from rest_framework.exceptions import APIException
from datetime import datetime

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler
from rest_framework.exceptions import ValidationError

class ResourceNotFoundException(APIException):
    status_code = 404
    default_detail = "Resource not found"
    default_code = "RESOURCE_NOT_FOUND"


class DuplicateResourceException(APIException):
    status_code = 409
    default_detail = "Duplicate resource"
    default_code = "DUPLICATE_RESOURCE"


class InsufficientInventoryException(APIException):
    status_code = 422
    default_detail = "Insufficient inventory"
    default_code = "INSUFFICIENT_INVENTORY"


class InvalidOperationException(APIException):
    status_code = 422
    default_detail = "Invalid operation"
    default_code = "INVALID_OPERATION"


class WarehouseHasActiveInventoryException(
    APIException
):
    status_code = 409

    default_detail = (
        "Warehouse has active inventory"
    )

    default_code = (
        "WAREHOUSE_HAS_ACTIVE_INVENTORY"
    )

def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    request = context.get("request")

    if response is None:
        return Response(
            {
                "timestamp": datetime.utcnow().isoformat(),
                "status": 500,
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "Internal server error",
                "path": request.path if request else "",
                "errors": [],
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    error_code = getattr(exc, "default_code", "ERROR")

    errors = []

    if isinstance(exc, ValidationError):
        error_code = "VALIDATION_FAILED"

        for field, messages in response.data.items():
            if isinstance(messages, list):
                for message in messages:
                    errors.append(
                        {
                            "field": field,
                            "message": str(message),
                        }
                    )

    response.data = {
        "timestamp": datetime.utcnow().isoformat(),
        "status": response.status_code,
        "error_code": error_code,
        "message": str(getattr(exc, "detail", "Error")),
        "path": request.path if request else "",
        "errors": errors,
    }

    return response