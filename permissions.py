from rest_framework import permissions


class IsJobBoardAdmin(permissions.BasePermission):
    """
    Custom permission to only allow JobBoard Admins to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is a JobBoard Admin
        return request.user and request.user.role == "admin"


class IsEmployer(permissions.BasePermission):
    """
    Custom permission to only allow Employers to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is an Employer
        print(
            f"User: {request.user}, Role: {getattr(request.user, 'role', None)}"
        )  # Debugging
        return request.user and request.user.role == "employer"


class IsJobseeker(permissions.BasePermission):
    """
    Custom permission to only allow Jobseekers to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is a Jobseeker
        print(f"User role(IsJobseeker): {getattr(request.user, 'role', None)}")
        return request.user and request.user.role == "jobseeker"
