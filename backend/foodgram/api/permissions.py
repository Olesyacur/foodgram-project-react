from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrAdminOrReadOnly(BasePermission):
    """
    Доступ только автору, админу или только для чтения.
    """
    def has_object_permission(self, request, view, obj):
        return (
            request.method in SAFE_METHODS
            or  request.user.is_superuser
            or request.user == obj.author
        )
class IsAuthor(BasePermission):
    """
    Доступ только автору.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (
            request.user == obj.author)