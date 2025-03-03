from rest_framework import permissions


class IsJobBoardAdmin(permissions.BasePermission):
    """
    Custom permission to only allow JobBoard Admins to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is a JobBoard Admin
        return request.user and request.user.role == "JobBoardAdmin"


class IsEmployer(permissions.BasePermission):
    """
    Custom permission to only allow Employers to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is an Employer
        return request.user and request.user.role == "Employer"


class IsJobseeker(permissions.BasePermission):
    """
    Custom permission to only allow Jobseekers to access the view.
    """

    def has_permission(self, request, view):
        # Check if the user is a Jobseeker
        return request.user and request.user.role == "Jobseeker"
