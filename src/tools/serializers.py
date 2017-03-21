from rest_framework import serializers
from tools.tools import *


class WeatherGeneratorSerializer(serializers.Serializer):

    precip = serializers.ListField(
        child=serializers.FloatField(),
        required=True
    )
    s_rad = serializers.ListField(
        child=serializers.FloatField(),
        required=True
    )
    t_min = serializers.ListField(
        child=serializers.FloatField(),
        required=True
    )
    t_max = serializers.ListField(
        child=serializers.FloatField(),
        required=True
    )
    history_dates = serializers.ListField(
        child=serializers.DateField(),
        required=True
    )
    simulation_dates = serializers.ListField(
        child=serializers.DateField(),
        required=True
    )

    def validate(self, data):
        """
        Check lengths.
        """

        if len(data['precip']) != len(data['s_rad']) != len(data['t_min']) \
           != len(data['t_max']) != len(data['dates']):
            raise serializers.ValidationError("Not equal time series")
        return data

    def create(self, validated_data):

        return WeatherGenerator(**validated_data)
