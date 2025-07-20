from rest_framework import serializers


class AnalyticsChartQuerySerializer(serializers.Serializer):
    site_id = serializers.CharField(required=True)
    range = serializers.ChoiceField(choices=["daily", "hourly", "minute"], default="daily")