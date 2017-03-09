from rest_framework import serializers
from app.models import *
from django.contrib.auth.models import User

import json
from django.contrib.gis.geos import GEOSGeometry

class UserSerializer(serializers.ModelSerializer):
    datasets = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'datasets')


class DatasetSerializer(serializers.ModelSerializer):
    model_objects = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    user = serializers.ReadOnlyField(source='user.username')
    class Meta:
        model = Dataset
        fields = ('id', 'name', 'descr', 'model_objects', 'public', 'user', 'bbox')

class ModelObjectSerializer(serializers.ModelSerializer):
    properties = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = ModelObject
        fields = ('id', 'geom_type', 'object_type', 'properties', 'dataset')


class PropertySerializer(serializers.ModelSerializer):
    num_values = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    cat_values = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    ras_values = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    value_series = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    raster_series = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    class Meta:
        model = Prop
        fields = ('id', 'num_values', 'cat_values', 'ras_values', 'value_series',
                  'raster_series', 'model_object', 'property_type', 'value_type', 'name')



class PropertyBigSerializer(serializers.BaseSerializer):
    def to_representation(self, prop):
        dataset_id = prop.model_object.dataset.id
        dataset_name = prop.model_object.dataset.name
        model_object_id = prop.model_object.id
        model_object_name = prop.model_object.name
        model_object_type = prop.model_object.object_type.object_type
        model_object_geom_type = prop.model_object.geom_type.geom_type
        property_id = prop.id
        property_name = prop.name
        property_type = prop.property_type.property_type
        value_type = prop.value_type.value_type

        return {
            'dataset_id': dataset_id,
            'dataset_name': dataset_name,
            'model_object_name': model_object_name,
            'model_object_id': model_object_id,
            'model_object_type': model_object_type,
            'model_object_geom_type': model_object_geom_type,
            'property_type': property_type,
            'value_type': value_type,
            'property_id': property_id,
            'property_name': property_name
        }


class ModelObjectGeoJSONSerializer(serializers.BaseSerializer):
    def to_representation(self, model_object):
        if model_object.geom_type_id == 4:
            geometry = None
        else: 
            geometry = json.loads(model_object.geometry.json)

        feature = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": model_object.id,
                "name": model_object.name,
                "dataset_id": model_object.dataset.id,
                "dataset_name": model_object.dataset.name,
                "geom_type": model_object.geom_type.geom_type,
                "object_type": model_object.object_type.object_type,
                }
        }

        return feature
