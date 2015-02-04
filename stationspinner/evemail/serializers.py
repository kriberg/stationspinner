from rest_framework import serializers
from stationspinner.evemail.models import Mail
from stationspinner.libs.drf_extensions import JSONField


class MailSerializer(serializers.ModelSerializer):
    receivers = JSONField()
    class Meta:
        model = Mail
        fields = ('messageID', 'title', 'senderName', 'parsed_message', 'sentDate',
                  'read', 'receivers', 'relevancy')

