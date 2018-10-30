from rest_framework import permissions


class BlacklistPermission(permissions.BasePermission):
    """
    Global permission check for blacklisted IPs.
    """

    def has_permission(self, request, view):
        ip_addr = request.META['REMOTE_ADDR']
        blacklisted = Blacklist.objects.filter(ip_addr=ip_addr).exists()
        return not blacklisted


class AnonPermissionOnly(permissions.BasePermission):
    """
    Non-authenicated Users only
    """
    message = 'You are already authenticated. Please log out to try again.'

    def has_permission(self, request, view):
        return not request.user.is_authenticated()


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    message = 'You must be the owner of this content to change.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user


class IsContributorOrReadOnly(permissions.BasePermission):
    message = 'You must be the contributor of this content to change.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user in obj.project.contributors.all()


class IsInspectorOrReadOnly(permissions.BasePermission):
    message = 'You must be the inspector of this content to change.'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user == obj.project.inspector


class IsOwner(permissions.BasePermission):
    """
    Object-level permission to only allow owners of an object to edit it.
    Assumes the model instance has an `owner` attribute.
    """
    message = 'You must be the owner of this content to change.'

    def has_object_permission(self, request, view, obj):
        return obj.owner == request.user


class IsStaff(permissions.BasePermission):
    message = 'Only staff can verify projects'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_staff:
            return True
        else:
            return False


class IsAdmin(permissions.BasePermission):
    message = 'Only admin can change tags'

    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.is_admin:
            return True
        else:
            return False


class HasContributed(permissions.BasePermission):
    message = 'You must have contributed to this content to change.'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.contributor


class HasInspected(permissions.BasePermission):
    message = 'You must have inspected to this content to change.'

    def has_object_permission(self, request, view, obj):
        return request.user == obj.inspector
