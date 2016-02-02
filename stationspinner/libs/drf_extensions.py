from rest_framework import permissions, viewsets, serializers

class CapsulerPermission(permissions.IsAuthenticated):
    """
    Standard capsuler access permission. If the data was pulled from the api
    by one of the api keys registered to this user, this permission class will
    grant access to it.
    """
    def has_object_permission(self, request, view, obj):
        return request.user.is_owner(obj)


class CapsulerViewset(viewsets.ModelViewSet):
    permission_classes = [CapsulerPermission]

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class JSONField(serializers.Field):
    def to_representation(self, obj):
        return obj

    def to_internal_value(self, data):
        return data


class ValidatedIDsMixin(object):
    '''
    Use this mixin to get valid IDs for corporation or characters from request
    '''

    def filter_valid_IDs(self, params, user):
        ids = params.get(self.validation_lookup_key, '')

        if len(ids) > 0:
            ids = map(int, str(ids).split(','))
            valid, invalid = self.validation_class.objects.filter_valid(ids, user)
        else:
            valid = []
            invalid = []
        return valid, invalid