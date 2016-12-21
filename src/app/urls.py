from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns
from app import api_views
from app import views

urlpatterns = [
    url(r'^datatable/$', views.Table.as_view(), name='datatable'),
    url(r'^toolbox/$', views.Toolbox.as_view(), name='toolbox'),
    url(r'^list_datasets/$', views.DatasetList.as_view(), name='explorer'),
    url(r'^dataset_details/(?P<dataset_id>[0-9]+)$', views.DatasetDetails.as_view(), name='dataset_details'),
    url(r'^create_dataset/$', views.CreateDataset.as_view(), name='create_dataset'),
    url(r'^model_object_details/(?P<model_object_id>[0-9]+)$', views.ModelObjectDetails.as_view(), name='model_object_details'),
    url(r'^property_details/(?P<property_id>[0-9]+)$', views.PropertyDetails.as_view(), name='property_details'),
    url(r'^create_model_object/(?P<dataset_id>[0-9]+)$', views.CreateModelObject.as_view(), name='create_model_object'),
    url(r'^create_property/(?P<model_object_id>[0-9]+)$', views.PropertyForms.as_view(), name='create_property'),
    url(r'^add_single_value/(?P<model_object_id>[0-9]+)$', views.CreateSingleValue.as_view(), name='add_single_value'),
    url(r'^add_value_series/(?P<model_object_id>[0-9]+)$', views.CreateValueSeries.as_view(), name='add_value_series'),
    url(r'^add_single_raster/(?P<model_object_id>[0-9]+)$', views.CreateSingleRaster.as_view(), name='add_single_raster'),
    url(r'^add_raster_series/(?P<model_object_id>[0-9]+)$', views.CreateRasterSeries.as_view(), name='add_raster_series'),
]