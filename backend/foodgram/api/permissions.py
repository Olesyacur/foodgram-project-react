from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAdminOrReadOnly(BasePermission):
    """
    Разрешение на уровне объекта, позволяющее редактировать
    объект только админу.
    """
    def has_permission(self, request, view):
        return request.method in SAFE_METHODS or (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_superuser)
        )

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or (
            request.user.is_admin
            or request.user.is_superuser
        )


class IsAdmin(BasePermission):
    """
    Доступ только администраторам.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )

class IsAuthor(BasePermission):
    """
    Доступ только автору.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user == obj.author)
