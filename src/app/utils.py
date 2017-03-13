import json
import os
import pandas as pd
import numpy as np
import subprocess
import math
from django.core.files.storage import FileSystemStorage
from django.contrib.gis.geos import GEOSGeometry, Polygon
from django.contrib.gis.gdal import GDALRaster, DataSource
from django.conf import settings

from app import models

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
            geometry = json.loads(property_.sampled_feature.geometry.json)

        insertion = {
            "type": "Feature",
            "geometry": geometry,
            "properties": {
                "id": property_.id,
                "sampled_object": property_.sampled_feature_id,
                "sampling_object": property_.model_object_id,
                "property_type": property_.property_type.property_type,
                "value_type": property_.value_type.value_type,
            }
        }

        geojson['features'].append(insertion)

    return geojson

def raster_handler(files, *args, **kwargs):
    """ Returns merged transformed raster file """
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

def excel_handler(spreadsheet, *args, **kwargs):
    """ Returns array of values read from Excel column """
    storage = FileSystemStorage()
    filename = storage.save('excel_files/' + spreadsheet.name, spreadsheet)
    df = pd.read_excel(
        os.path.join(settings.MEDIA_ROOT, filename),
        header=None, sheetname=0
        )
    df = df.dropna()

    values = df[1].tolist()
    timestamps = df[0].tolist()

    os.remove(os.path.join(settings.MEDIA_ROOT, filename))

    return values, timestamps

def shape_handler(shapefile, *args, **kwargs):
    """ Returns list of GEOS geometry objects from the uploaded file """
    storage = FileSystemStorage()
    filename = storage.save('shape_files/' + shapefile.name, shapefile)
    ds = DataSource(
        os.path.join(settings.MEDIA_ROOT, filename),
        )
    features = ds[0].get_geoms()
    names = ds[0].get_fields('name')
    types = ds[0].get_fields('type')
    try:
        sampled_features = ds[0].get_fields('sampled_feature')
    except:
        sampled_features = [None for i in features]

    os.remove(os.path.join(settings.MEDIA_ROOT, filename))

    return features, names, types, sampled_features

def update_bbox(dataset_id):
    """ Recalculates dataset bbox and OSM tile index """

    dataset = models.Dataset.objects.get(id=dataset_id)
    features = models.ModelObject.objects.filter(
        dataset_id=dataset_id,
        geometry__isnull=False)
    if features:
        features_geoms = [i.geometry for i in features]

        top_right_xs = [i.extent[2] for i in features_geoms]
        top_right_ys = [i.extent[3] for i in features_geoms]
        botm_left_xs = [i.extent[0] for i in features_geoms]
        botm_left_ys = [i.extent[1] for i in features_geoms]

        bbox = [
            min(botm_left_xs),
            min(botm_left_ys),
            max(top_right_xs),
            max(top_right_ys)
        ]
        dataset.bbox = Polygon.from_bbox(bbox)
        dataset.tile_url = calculate_tile_index(
            bbox_geom=(dataset.bbox),
            as_url=True
            )
        dataset.save()


def calculate_tile_index(bbox_geom, as_url):
    """ Returnes x, y, z indexes for openstreet tile servers """
    if bbox_geom is None:
         zoom_level, xtile, ytile = 0, 0, 0
    else:
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
