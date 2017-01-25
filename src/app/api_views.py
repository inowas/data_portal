from app.models import *
from django.contrib.auth.models import User
from django.contrib.gis.geos import GEOSGeometry
from app.serializers import *
from rest_framework import generics
from rest_framework import permissions
from rest_framework.decorators import api_view
from rest_framework.response import Response
from app.permissions import IsOwnerOrReadOnly


class UserList(generics.ListCreateAPIView):
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class DatasetList(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
        )

    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class DatasetDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Dataset.objects.all()
    serializer_class = DatasetSerializer


class ModelObjectList(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        )

    serializer_class = ModelObjectSerializer

    def get_queryset(self):
        dataset = self.request.query_params.get('dataset', None)
        geom_type = self.request.query_params.get('geom_type')
        object_type = self.request.query_params.get('object_type')
        q = ModelObject.objects.all()
        if dataset is not None:
            q = q.filter(dataset_id=dataset)
        if geom_type is not None:
            q = q.filter(geom_type=geom_type)
        if object_type is not None:
            q = q.filter(object_type=object_type)
        return q


class ModelObjectDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = ModelObject.objects.all()
    serializer_class = ModelObjectSerializer

class PropertyList(generics.ListCreateAPIView):
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsOwnerOrReadOnly
        )

    queryset = Prop.objects.all()
    serializer_class = PropertySerializer


class PropertytDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Prop.objects.all()
    serializer_class = PropertySerializer


@api_view(['GET'])
def property_big_list(request):
    bbox_wkt = request.query_params.get('bbox', None)
    queryset = Prop.objects.all()
    if bbox_wkt is not None:
        bbox = GEOSGeometry(bbox_wkt, srid=3857)
        queryset = queryset.filter(model_object__bbox__intersects=bbox)

    serializer = PropertyBigSerializer(queryset, many=True)
    return Response(serializer.data)

# @api_view(['GET'])
# def dataset_tree(request, pk):
#     try:
#         queryset = Dataset.objects.get(id=pk)
#     except Dataset.DoesNotExist:
#         return Response({
#             "detail": "Not found."
#         })

#     serializer = TreeSerializer(queryset, many=False)
#     return Response(serializer.data)

@api_view(['GET'])
def get_geojson_all(request):
    queryset = ModelObject.objects.all()

    serializer = ModelObjectGeoJSONSerializer(queryset, many=True)
    features = serializer.data
    return Response(
        {"type": "FeatureCollection",
         "crs": {
             "type": "name",
             "properties": {
                 "name": "EPSG:3857"
             }
         },
         "features": features}
    )

@api_view(['GET'])
def get_geojson_dataset(request, pk):

    queryset = ModelObject.objects.filter(dataset_id=pk)

    serializer = ModelObjectGeoJSONSerializer(queryset, many=True)
    features = serializer.data
    return Response(
        {"type": "FeatureCollection",
         "crs": {
             "type": "name",
             "properties": {
                 "name": "EPSG:3857"
                 }
         },
         "features": features}
    )

@api_view(['GET'])
def get_geojson_feature(request, pk):

    queryset = ModelObject.objects.filter(id=pk)

    serializer = ModelObjectGeoJSONSerializer(queryset, many=True)
    features = serializer.data
    return Response(
        {"type": "FeatureCollection",
         "crs": {
             "type": "name",
             "properties": {
                 "name": "EPSG:3857"
                 }
         },
         "features": features}
    )
