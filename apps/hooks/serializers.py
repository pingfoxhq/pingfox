from rest_framework import serializers

class WebhookEventSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.CharField()
    timestamp = serializers.DateTimeField()
    team_id = serializers.CharField()
    site_id = serializers.CharField(allow_null=True, required=False)
    data = serializers.DictField()
