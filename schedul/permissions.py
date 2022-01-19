from rest_framework import permissions

class IsActiveUser(permissions.BasePermission):
    
    def has_object_permission(self, request, view, obj):
        user = request.user
        # X: user.schedul.is_confirmed
        return user.is_authenticated and user.is_active


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

