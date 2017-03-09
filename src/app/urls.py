from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from app import api_views
from app import views

urlpatterns = [
    # url(r'^toolbox/$', views.toolbox, name='toolbox'),
    url(r'^datatable/$', views.Table.as_view(), name='datatable'),
    # url(r'^toolbox/$', views.Toolbox.as_view(), name='toolbox'),
    url(r'^datacollections/$', views.DatasetList.as_view(), name='explorer'),
    url(r'^dataset-details/(?P<dataset_id>[0-9]+)$', views.DatasetDetails.as_view(), name='dataset-details'),
    url(r'^feature-details/(?P<model_object_id>[0-9]+)$', views.ModelObjectDetails.as_view(), name='feature-details'),
    url(r'^property-details/(?P<property_id>[0-9]+)$', views.PropertyDetails.as_view(), name='property-details'),
    url(r'^add-dataset/$', views.CreateDataset.as_view(), name='add-dataset'),
    url(r'^add-feature/(?P<dataset_id>[0-9]+)$', views.CreateModelObject.as_view(), name='add-feature'),
    url(r'^upload-feature/(?P<dataset_id>[0-9]+)$', views.CreateModelObjectsUpload.as_view(), name='upload-feature'),
    url(r'^add-single-value/(?P<model_object_id>[0-9]+)$', views.CreateSingleValue.as_view(), name='add-single-value'),
    url(r'^add-value-series/(?P<model_object_id>[0-9]+)$', views.CreateValueSeries.as_view(), name='add-value-series'),
    url(r'^upload-value-series/(?P<model_object_id>[0-9]+)$', views.CreateValueSeriesUpload.as_view(), name='upload-value-series'),
    url(r'^add-single-raster/(?P<model_object_id>[0-9]+)$', views.CreateSingleRaster.as_view(), name='add-single-raster'),
    url(r'^add-raster-series/(?P<model_object_id>[0-9]+)$', views.CreateRasterSeries.as_view(), name='add-raster-series'),
    url(r'^update-dataset/(?P<dataset_id>[0-9]+)$', views.UpdateDataset.as_view(), name='update-dataset'),
]