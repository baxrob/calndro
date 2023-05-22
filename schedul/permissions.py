from rest_framework import permissions


class IsEventPartyOrAdmin(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        if request.method == 'OPTIONS':
            # Hack for DRF HTML view magic
            if isinstance(obj, type({})) and 'event' in obj:
                obj = obj['event']
        if request.method == 'DELETE':
            return request.user.is_staff
        return (
            request.user.is_staff
            or request.user.is_authenticated
            and request.user.email in [p.email for p in obj.parties.all()]
        )

