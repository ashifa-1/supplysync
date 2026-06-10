from rest_framework.permissions import BasePermission

from apps.accounts.models import UserRole


class IsAdminUser(BasePermission):
    message = (
        "Only administrators can perform this action."
    )

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role == UserRole.ADMIN
        )


class IsWarehouseManagerOrAdmin(
    BasePermission
):
    message = (
        "Only warehouse managers or administrators "
        "can perform this action."
    )

    def has_permission(
        self,
        request,
        view
    ):
        return (
            request.user.is_authenticated
            and request.user.role in [
                UserRole.ADMIN,
                UserRole.WAREHOUSE_MANAGER,
            ]
        )


class IsProcurementManagerOrAdmin(
    BasePermission
):
    message = (
        "Only procurement managers or administrators "
        "can perform this action."
    )

    def has_permission(
        self,
        request,
        view
    ):
        return (
            request.user.is_authenticated
            and request.user.role in [
                UserRole.ADMIN,
                UserRole.PROCUREMENT_MANAGER,
            ]
        )


class IsWarehouseManagerOrAdminOrStaff(
    BasePermission
):
    message = (
        "Only warehouse managers, staff, or "
        "administrators can perform this action."
    )

    def has_permission(
        self,
        request,
        view
    ):
        return (
            request.user.is_authenticated
            and request.user.role in [
                UserRole.ADMIN,
                UserRole.WAREHOUSE_MANAGER,
                UserRole.STAFF,
            ]
        )


class IsOwnerOrAdmin(BasePermission):
    message = (
        "You can only access your own objects."
    )

    def has_object_permission(
        self,
        request,
        view,
        obj
    ):
        if (
            request.user.role
            == UserRole.ADMIN
        ):
            return True

        owner = getattr(
            obj,
            "created_by",
            None
        )

        if owner is None:
            owner = getattr(
                obj,
                "performed_by",
                None
            )

        return owner == request.user