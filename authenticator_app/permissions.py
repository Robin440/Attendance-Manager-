from rest_framework.permissions import BasePermission

class IsRoleAdmin(BasePermission):
   
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
       
        return request.user.shift_manager_members.filter(role__name='admin').exists()
