from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.renderers import JSONRenderer
import json
from tools.tools import *
from tools.serializers import *


class WeatherGeneratorView(APIView):
    """ Weather generator tool API view """

    def post(self, request, *args, **kw):

        serializer = WeatherGeneratorSerializer(data=request.data)

        if serializer.is_valid():
            generator = serializer.save()
            generator.generate_precipitation()
            generator.generate_temperatures()

            return Response(
                {
                    "simulation_dates": generator.simulation_dates_original,
                    "simulated_precip": generator.simulated_precip.tolist(),
                    "simulated_t_min": generator.simulated_t_min.tolist(),
                    "simulated_t_max": generator.simulated_t_max.tolist(),
                    "simulated_s_rad": generator.simulated_s_rad.tolist()
                }

            )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



