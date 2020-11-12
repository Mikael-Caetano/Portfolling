from rest_framework import permissions 


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    A permission checker to the API. Returns `True` if the request method is a safe method or if the request user is the owner of the related Portfoller instance.
    """
    message = 'Not the profile owner'

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        try:
            #To check permission in PortfollerViewset
            return request.user.username == obj.username or request.user.is_superuser
        except AttributeError:
            try:
                #To check permission in ProjectViewset
                return request.user.username == obj.user.username or request.user.is_superuser
            except AttributeError:
                #To check permission in ProjectImageViewset
                return request.user.username == obj.project.user.username or request.user.is_superuser
