from rest_framework.permissions import BasePermission

class IsAdmin(BasePermission):
    """"
    Allows access only to admin users.
    Django admin == is_staff=True
    """

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_staff)
