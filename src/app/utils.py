import json
import os
import pandas as pd
import subprocess
import math
from django.core.files.storage import FileSystemStorage
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.contrib.gis.gdal import GDALRaster
from django.conf import settings

from app import models

def set_geometry(geom_type, model_object, geom_wkt):
    """ Returns MO bbox ands sets specific geometry """
    if geom_type.geom_type == 'linestring':
        geom_object = models.LineObject(
            model_object=model_object,
            geometry=GEOSGeometry(geom_wkt)
        )

    elif geom_type.geom_type == 'point':
        geom_object =models.PointObject(
            model_object=model_object,
            geometry=GEOSGeometry(geom_wkt)
        )

    elif geom_type.geom_type == 'polygon':
        geom_object = models.PolygonObject(
            model_object=model_object,
            geometry=GEOSGeometry(geom_wkt)
        )

    elif geom_type.geom_type == 'compound':
        geom_object = models.CompoundObject(
            model_object=model_object,
            geometry=None
        )
        geom_object.save()
        return None

    geom_object.save()

    buffer = GEOSGeometry(geom_wkt).buffer(1)
    bbox = buffer.envelope

    return bbox

def get_geojson(model_objects):
    """ Returnes GeoJSON views for given model objects """
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }

    for model_object in model_objects:
        geom_type = model_object.geom_type.geom_type

        if geom_type == 'point':
            geom_obj = models.PointObject.objects.get(model_object_id=model_object.id)
            geometry = json.loads(geom_obj.geometry.json)
        elif geom_type == 'linestring':
            geom_obj = models.LineObject.objects.get(model_object_id=model_object.id)
            geometry = json.loads(geom_obj.geometry.json)
        elif geom_type == 'polygon':
            geom_obj = models.PolygonObject.objects.get(model_object_id=model_object.id)
            geometry = json.loads(geom_obj.geometry.json)
        else:
            geometry = json.loads('{"type": "Point", "coordinates": []}')

        insertion = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": model_object.id,
                "dataset_id": model_object.dataset.id,
                "geom_type": geom_type,
                "object_type": model_object.object_type.object_type,
                "properties": [i.property_type.property_type for i in model_object.properties.all()],
                }
        }

        geojson['features'].append(insertion)

    return geojson

def get_specific_geometry(model_object):

    geom_type = model_object.geom_type.geom_type
    if geom_type == 'point':
        geom_obj = models.PointObject.objects.get(model_object_id=model_object.id)
        geometry = json.loads(geom_obj.geometry.json)
    elif geom_type == 'linestring':
        geom_obj = models.LineObject.objects.get(model_object_id=model_object.id)
        geometry = json.loads(geom_obj.geometry.json)
    elif geom_type == 'polygon':
        geom_obj = models.PolygonObject.objects.get(model_object_id=model_object.id)
        geometry = json.loads(geom_obj.geometry.json)
    else:
        geometry = json.loads('{"type": "Point", "coordinates": []}')

    return geometry

def get_specific_value(property_):

    value_type = property_.value_type.value_type
    if value_type == 'numerical':
        value_object = models.NumValue.objects.get(prop_id=property_.id)
        value_id = value_object.id
        value = value_object.value
    elif value_type == 'categorical':
        value_object = models.CatValue.objects.get(prop_id=property_.id)
        value_id = value_object.id
        value = value_object.value
    elif value_type == 'raster':
        value_object = models.RasValue.objects.get(prop_id=property_.id)
        value_id = value_object.id
        value = value_object.value
    elif value_type == 'time_series':
        value_object = models.ValueSeries.objects.get(prop_id=property_.id)
        value_id = value_object.id
        value = value_object.value
    elif value_type == 'raster_series':
        value_object = models.RasterSeries.objects.get(prop_id=property_.id)
        value_id = value_object.id
        value = value_object.value

    return value_id, value

def get_prop_geojson(properties):
    """ Returnes GeoJSON views for given properties """
    geojson = {
        "type": "FeatureCollection",
        "features": []
    }
    
    for property_ in properties:
        if property_.obs_point is None:
            geometry = get_specific_geometry(property_.model_object)
        else:
            geometry = json.loads(property_.obs_point.geometry.json)

        insertion = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": property_.id,
                "observerd_at_point": property_.obs_point_id,
                "object_id": property_.model_object_id,
                "property_type": property_.property_type.property_type,
                "value_type": property_.value_type.value_type,
            }
        }

        geojson['features'].append(insertion)

    return geojson

def raster_handler(files, *args, **kwargs):

    rasters_dir = os.path.join(settings.MEDIA_ROOT, 'rasters')
    if len(files) > 1:
        output_raster = os.path.join(rasters_dir, 'merged.tif')
        if os.path.isfile(output_raster):
            os.remove(output_raster)

        merge_command = ["python", "utils/gdal_merge.py", "-o", output_raster, "-separate"]
        rasters = []

        for f in files:
            storage = FileSystemStorage()
            filename = storage.save('rasters/' + f.name, f)
            rasters.append(os.path.join(settings.MEDIA_ROOT, filename))

        merge_command += rasters

        subprocess.call(merge_command)

        for f in rasters:
            os.remove(f)

        source = GDALRaster(output_raster, write=True)
    
    elif len(files) == 1:
        storage = FileSystemStorage()
        filename = storage.save('rasters/' + files[0].name, files[0])

        source = GDALRaster(os.path.join(settings.MEDIA_ROOT, filename), write=True)

    return source.transform(3857)

def update_bbox(bbox_geom, feature_geom):
    """ Returnes updated bbox including new feat. geom. """
    if feature_geom is None:
        return bbox_geom
    
    extent_1 = bbox_geom.extent
    extent_2 = feature_geom.extent
    bbox_updated = [
        min(extent_1[0], extent_2[0]),
        min(extent_1[1], extent_2[1]),
        max(extent_1[2], extent_2[2]),
        max(extent_1[3], extent_2[3])
    ]

    return Polygon.from_bbox(bbox_updated)

def calculate_tile_index(bbox_geom, as_url):
    """ Returnes x, y, z indexes for openstreet tile servers """
    if bbox_geom is None:
        return 0, 0, 0
    bbox_geom = bbox_geom.transform(4326, clone=True)
    extent = bbox_geom.extent
    max_extent = max(
        abs(extent[2] - extent[0]),
        abs(extent[3] - extent[1]) * 2
        )
    lon_deg = .5 * (extent[2] + extent[0])
    lat_deg = .5 * (extent[3] + extent[1])

    if max_extent < .352:
        max_extent = .352

    zoom_level = int(round(math.log2(360/max_extent)))
    lat_rad = math.radians(lat_deg)
    n = 2.0 ** zoom_level
    xtile = int((lon_deg + 180.0) / 360.0 * n)
    ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)

    if as_url:
        return 'https://a.tile.openstreetmap.org' + \
               '/' + str(zoom_level) + '/' + str(xtile) + '/' +str(ytile) + '.png'
    else:
        return zoom_level, xtile, ytile



