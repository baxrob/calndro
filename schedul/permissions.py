from rest_framework import permissions

class IsEventParty(permissions.BasePermission):

    def has_object_permissions(self, request, view, obj):
        pass
