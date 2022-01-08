from rest_framework import permissions

class IsEventPartyOrAdmin(permissions.BasePermission):
    #message = 
    #code =

    def has_object_permission(self, request, view, obj):
        #import ipdb; ipdb.set_trace()
        return (
            request.user.is_superuser
            or request.user.is_authenticated
            and request.user.email in [p.email for p in obj.parties.all()]
        )

