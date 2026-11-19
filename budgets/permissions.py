from rest_framework.permissions import SAFE_METHODS, BasePermission, DjangoModelPermissions


class FullDjangoModelPermissions(DjangoModelPermissions):
    """Like DjangoModelPermissions, but reading also requires the view_ permission."""
    perms_map = {
        **DjangoModelPermissions.perms_map,
        "GET": ["%(app_label)s.view_%(model_name)s"],
    }


class IsCreatorOrSuperuser(BasePermission):
    """Only the expense creator (or a superuser) can update or delete it."""

    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return request.user.is_superuser or obj.created_by_id == request.user.id