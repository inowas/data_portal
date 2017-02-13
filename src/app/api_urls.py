from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from app import api_views
from app import views

urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls',namespace='rest_framework')),
    url(r'^users/$', api_views.UserList.as_view()),
    url(r'^users/(?P<pk>[0-9]+)$', api_views.UserDetail.as_view()),
    url(r'^datasets/$', api_views.DatasetList.as_view()),
    url(r'^datasets/(?P<pk>[0-9]+)$', api_views.DatasetDetail.as_view()),
    url(r'^modelobjects/$', api_views.ModelObjectList.as_view()),
    url(r'^modelobjects/(?P<pk>[0-9]+)$', api_views.ModelObjectDetail.as_view()),
    url(r'^properties/$', api_views.PropertyList.as_view()),
    url(r'^properties/(?P<pk>[0-9]+)$', api_views.PropertytDetail.as_view()),
    url(r'^properties-long/$', api_views.property_big_list),
    url(r'^geojson/$', api_views.get_geojson_all),
    url(r'^geojson-dataset/(?P<pk>[0-9]+)$', api_views.get_geojson_dataset),
    url(r'^geojson-feature/(?P<pk>[0-9]+)$', api_views.get_geojson_feature),
]

urlpatterns = format_suffix_patterns(urlpatterns)