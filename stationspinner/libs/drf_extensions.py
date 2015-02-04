from rest_framework import permissions, viewsets, serializers
import json

class CapsulerPermission(permissions.BasePermission):
    """
    Standard capsuler access permission. If the data was pulled from the api
    by one of the api keys registered to this user, this permission class will
    grant access to it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_owner(obj)

    def has_permission(self, request, view):
        return True


class CapsulerViewset(viewsets.ModelViewSet):
    permission_classes = [CapsulerPermission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class JSONField(serializers.Field):
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data