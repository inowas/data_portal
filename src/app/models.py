"""
Definition of models.
"""

from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField


class GeomType(models.Model):
    """ """
    geom_type = models.TextField()

    def __str__(self):
        return '%s' % (self.geom_type)


class ObjectType(models.Model):
    """ """
    object_type = models.TextField()

    def __str__(self):
        return '%s' % (self.object_type)

class PropertyType(models.Model):
    """ """
    property_type = models.TextField()

    def __str__(self):
        return '%s' % (self.property_type)

class ValueType(models.Model):
    """ """
    value_type = models.TextField()

    def __str__(self):
        return '%s' % (self.value_type)



class Dataset(models.Model):
    """ """
    user = models.ForeignKey('auth.User', on_delete=models.CASCADE, related_name='datasets')
    public = models.BooleanField(default=True)
    name = models.CharField(max_length=20)
    descr = models.TextField()
    bbox = models.PolygonField(srid=3857, blank=True, null=True)
    tile_url = models.TextField(default='https://a.tile.openstreetmap.org/0/0/0.png')
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return '%s %s' % (self.name, self.id)


class ModelObject(models.Model):
    """ """
    name = models.TextField(default='Noname')

    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE,
        related_name='model_objects')

    geom_type = models.ForeignKey(
        GeomType, on_delete=models.CASCADE,
        related_name='model_objects')

    object_type = models.ForeignKey(
        ObjectType, on_delete=models.CASCADE,
        related_name='model_objects')

    geometry = models.GeometryField(srid=3857,
        blank=True, null=True)

    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return '%s %s' % (self.object_type, self.id)


class Prop(models.Model):

    """ """
    model_object = models.ForeignKey(
        ModelObject, on_delete=models.CASCADE,
        related_name='properties',
        null=True
        )
    # obs_point = models.ForeignKey(
    #     PointObject, on_delete=models.CASCADE,
    #     related_name='observed_properties',
    #     blank=True, null=True
    #     )
    property_type = models.ForeignKey(
        PropertyType, on_delete=models.CASCADE,
        related_name='properties',
        null=True)

    value_type = models.ForeignKey(
        ValueType, on_delete=models.CASCADE,
        related_name='properties',
        null=True)
    timestart = models.DateTimeField(null=True, blank=True)
    interval = models.DurationField(null=True, blank=True)
    num_vals = models.IntegerField(default=1)
    name = models.TextField(default='Noname')

    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return '%s %s' % (self.property_type, self.id)


class NumValue(models.Model):
    """ """
    prop = models.ForeignKey(
        Prop, on_delete=models.CASCADE,
        related_name='num_values'
        )

    value = models.FloatField(null=True)

    def __str__(self):
        return '%s' % (self.value)


class CatValue(models.Model):
    """ """
    prop = models.ForeignKey(
        Prop, on_delete=models.CASCADE,
        related_name='cat_values'
        )

    value = models.CharField(max_length=20, null=True)


    def __str__(self):
        return '%s' % (self.value)


class RasValue(models.Model):
    """ """
    prop = models.ForeignKey(
        Prop, on_delete=models.CASCADE,
        related_name='ras_values'
        )
    value = models.RasterField(srid=3857, null=True)


    def __str__(self):
        return 'raster, %s' % (self.id)

class ValueSeries(models.Model):
    """ """
    prop = models.ForeignKey(
        Prop, on_delete=models.CASCADE,
        related_name='value_series'
        )

    value = ArrayField(models.FloatField(null=True), null=True)

    def __str__(self):
        return '%s %s' % (self.timestart, self.interval)


class RasterSeries(models.Model):
    """ """
    prop = models.ForeignKey(
        Prop, on_delete=models.CASCADE,
        related_name='raster_series'
        )

    value = models.RasterField(srid=3857)

    def __str__(self):
        return '%s %s' % (str(self.timestart), str(self.interval))