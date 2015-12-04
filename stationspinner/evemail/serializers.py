from rest_framework import serializers
from stationspinner.evemail.models import Mail, MailStatus
from stationspinner.libs.drf_extensions import JSONField


class MailSerializer(serializers.ModelSerializer):
    receivers = JSONField()
    class Meta(object):
        model = Mail
        fields = ('messageID', 'title', 'senderName', 'parsed_message', 'sentDate',
                  'read', 'receivers', 'relevancy')


class MailStatusSerializer(serializers.ModelSerializer):
    messageID = serializers.IntegerField(read_only=True)
    class Meta(object):
        model = MailStatus
        fields = ('messageID', 'read')