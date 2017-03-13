"""
Definition of models.
"""

from django.contrib.gis.db import models
from django.contrib.postgres.fields import ArrayField
# from taggit.managers import TaggableManager


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
    name = models.CharField(max_length=100)
    descr = models.TextField(max_length=300)
    bbox = models.PolygonField(srid=3857, blank=True, null=True)
    tile_url = models.TextField(default='https://a.tile.openstreetmap.org/0/0/0.png')
    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)
    # tags = TaggableManager()

    def __str__(self):
        return '%s %s' % (self.name, self.id)


class ModelObject(models.Model):
    """ """
    name = models.CharField(
        max_length=100,
        default='Noname'
        )

    sampled_feature = models.ForeignKey(
        "self", on_delete=models.SET_NULL,
        related_name='sampling_feature',
        blank=True, null=True,
        )

    dataset = models.ForeignKey(
        Dataset, on_delete=models.CASCADE,
        related_name='model_objects')

    geom_type = models.ForeignKey(
        GeomType, on_delete=models.CASCADE,
        related_name='model_objects')

    object_type = models.ForeignKey(
        ObjectType, on_delete=models.CASCADE,
        related_name='model_objects')

    geometry = models.GeometryField(
        srid=3857,
        blank=True, null=True
        )

    created = models.DateTimeField(auto_now_add=True, null=True)
    modified = models.DateTimeField(auto_now=True, null=True)

    def __str__(self):
        return '%s %s' % (self.name, self.object_type)


class Prop(models.Model):

    """ """
    model_object = models.ForeignKey(
        ModelObject, on_delete=models.CASCADE,
        related_name='properties',
        null=True
        )

    property_type = models.ForeignKey(
        PropertyType, on_delete=models.CASCADE,
        related_name='properties',
        null=True)

    value_type = models.ForeignKey(
        ValueType, on_delete=models.CASCADE,
        related_name='properties',
        null=True)

    name = models.CharField(max_length=100)

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
    timestamps = ArrayField(models.DateTimeField(null=True), null=True)

    def __str__(self):
        return '%s %s' % (self.id)


class RasterSeries(models.Model):
    """ """
    prop = models.ForeignKey(
        Prop, on_delete=models.CASCADE,
        related_name='raster_series'
        )

    value = models.RasterField(srid=3857)
    timestamps = ArrayField(models.DateTimeField(null=True), null=True)

    def __str__(self):
        return '%s %s' % (self.id)