from django.conf.urls import url, include
from rest_framework.urlpatterns import format_suffix_patterns
from tools import api_views


urlpatterns = [
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^weather-generator-v-1/$', api_views.WeatherGeneratorView.as_view(), name='weather_generator'),
]

urlpatterns = format_suffix_patterns(urlpatterns)