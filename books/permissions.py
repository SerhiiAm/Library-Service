from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    The request is anonymous or authenticated for read-only request,
    or authenticated as an admin (is_staff) for read/write.
    """

    def has_permission(self, request, view) -> bool:
        return bool(
            request.method in SAFE_METHODS
            or (request.user and request.user.is_staff)
        )
