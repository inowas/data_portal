"""
Definition of views.
"""
from datetime import datetime
import os

from django.urls import reverse
from django.views import View
from django.shortcuts import render, redirect
from django.http import HttpRequest, Http404
from django.views.generic.edit import FormView, CreateView
from django.views.generic.base import TemplateView
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import GEOSGeometry

from app.models import *
from app.forms import *
from app.utils import *
from app.vis.bokeh_plots import *



class Table(View):

    def get(self, request):
        return render(request, 'app/datatable.html')


class Toolbox(View):

    def get(self, request):
        return render(request, 'app/toolbox.html')

class DatasetList(View):

    def get(self, request):
        datasets = Dataset.objects.all()
        return render(request, 'app/datasets_explorer.html', {'datasets': datasets})


class DatasetDetails(View):

    def get(self, request, dataset_id):
        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            raise Http404("Dataset does not exist")

        model_objects = ModelObject.objects.filter(dataset=dataset)

        return render(
            request, 'app/details_dataset.html',
            {
                'dataset': dataset,
                'model_objects': model_objects,
                'geojson_url': '/api/geojson-dataset/' + str(dataset.id)
            }
        )

class ModelObjectDetails(View):

    def get(self, request, model_object_id):
        try:
            model_object = ModelObject.objects.get(id=model_object_id)
        except ModelObject.DoesNotExist:
            raise Http404("Object does not exist")
        dataset = Dataset.objects.get(id=model_object.dataset_id)

        properties = Prop.objects.filter(model_object=model_object)

        return render(
            request, 'app/details_feature.html',
            {
                'dataset': dataset,
                'model_object': model_object,
                'properties': properties,
                'geojson_url': '/api/geojson-feature/' + str(model_object.id)
            }
        )


class PropertyDetails(View):

    def get(self, request, property_id):
        try:
            prop = Prop.objects.get(id=property_id)
        except Prop.DoesNotExist:
            raise Http404("Property does not exist")

        model_object = prop.model_object
        dataset = prop.model_object.dataset

        if prop.value_type.value_type == 'numerical':
            try:
                value = NumValue.objects.get(prop=prop)
            except NumValue.DoesNotExist:
                raise Http404("Property does not exist")

            controls, raster_map, plot, table, script = None, None, None, None, None
            descr = 'single numerical value'
            value = str(value.value)

        elif prop.value_type.value_type == 'categorical':
            try:
                value = CatValue.objects.get(prop=prop)
            except CatValue.DoesNotExist:
                raise Http404("Property does not exist")
            controls, raster_map, plot, table, script = None, None, None, None, None
            descr = 'single numerical value'
            value = str(value.value)

        elif prop.value_type.value_type == 'value_time_series':
            try:
                values = ValueSeries.objects.get(prop=prop)
            except ValueSeries.DoesNotExist:
                raise Http404("Property does not exist")

            script, div = plot_time_series(
                values, timestart=prop.timestart, interval=prop.interval,
                plot_width=500, plot_height=500,
                table_width=550, table_height=550
                )

            controls, raster_map, plot, table = None, None, div['plot'], div['table']
            descr = 'time-series of values'
            value = None

        elif prop.value_type.value_type == 'raster':
            try:
                raster = RasValue.objects.get(prop=prop)
            except RasValue.DoesNotExist:
                raise Http404("Property does not exist")

            script, div = plot_single_raster(
                raster, resize_coef=0.1, plot_width=500, plot_height=500,
                table_width=550, table_height=550
                )
            controls, raster_map, plot, table = None, div['raster_map'], div['plot'], None
            descr = 'singe raster'
            value = None

        elif prop.value_type.value_type == 'raster_time_series':
            try:
                raster = RasterSeries.objects.get(prop=prop)
            except RasterSeries.DoesNotExist:
                raise Http404("Property does not exist")

            script, div = plot_raster_series(
                raster, resize_coef=0.1, plot_width=500, plot_height=500,
                table_width=550, table_height=550
                )
            controls, raster_map, plot, table = div['controls'],\
            div['raster_map'], div['plot'], None

            descr = 'time-series of rasters'
            value = None

        return render(
            request, 'app/details_property.html',
            {
                'descr': descr,
                'value': value,
                'script': script,
                'plot': plot,
                'table': table,
                'raster_map': raster_map,
                'controls': controls,
                'dataset': dataset,
                'model_object': model_object,
                'prop': prop
                }
            )


class CreateModelObject(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_add_feature.html'
    form_class = ModelObjectForm
    success_url = '/dataset-details/'

    @transaction.atomic
    def form_valid(self, form):
        dataset_id = self.kwargs['dataset_id']
        wkt = self.request.POST['geometry']
        self.success_url += dataset_id

        model_object = form.save(commit=False)
        model_object.dataset_id = dataset_id
        if wkt:
            model_object.geometry = GEOSGeometry(wkt)
            if GEOSGeometry(wkt).geom_type == 'Point':
                model_object.geom_type_id = 1
            if GEOSGeometry(wkt).geom_type == 'LineString':
                model_object.geom_type_id = 2
            if GEOSGeometry(wkt).geom_type == 'Polygon':
                model_object.geom_type_id = 3
        else:
            model_object.geometry = None
            model_object.geom_type_id = 4

        model_object.save()

        dataset = Dataset.objects.get(id=dataset_id)
        if dataset.bbox is None:
            buffer = model_object.geometry.buffer(1)
            bbox = buffer.envelope
            dataset.bbox = bbox
        else:
            dataset.bbox = update_bbox(bbox_geom=dataset.bbox,
                                       feature_geom=model_object.geometry)
        dataset.tile_url = calculate_tile_index(bbox_geom=dataset.bbox,
                                                as_url=True)
        dataset.save()

        return super(CreateModelObject, self).form_valid(form)


class CreateModelObjectsUpload(LoginRequiredMixin, FormView):
    template_name = 'app/create_forms/form_template_geojson_upload.html'
    form_class = ModelObjectUploadForm
    success_url = '/dataset-details/'

    @transaction.atomic
    def form_valid(self, form):
        dataset_id = self.kwargs['dataset_id']
        self.success_url += dataset_id

        files = self.get_form_kwargs().get('files').getlist('file_field')
        features, names, types = shape_handler(files[0])
        for f, n, t in zip(features, names, types):
            if f.geom_type == 'Point':
                geom_type_id = 1
            elif f.geom_type == 'LineString':
                geom_type_id = 2
            elif f.geom_type == 'Polygon':
                geom_type_id = 3

            model_object = ModelObject(
                geometry=f.geos,
                name=n,
                object_type=ObjectType.objects.get(object_type=t),
                dataset_id=dataset_id,
                geom_type_id=geom_type_id
            )

            model_object.save()

            dataset = Dataset.objects.get(id=dataset_id)
            if dataset.bbox is None:
                buffer = model_object.geometry.buffer(1)
                bbox = buffer.envelope
                dataset.bbox = bbox
            else:
                dataset.bbox = update_bbox(bbox_geom=dataset.bbox,
                                           feature_geom=model_object.geometry)
            dataset.tile_url = calculate_tile_index(bbox_geom=dataset.bbox,
                                                    as_url=True)
            dataset.save()

        return super(CreateModelObjectsUpload, self).form_valid(form)

class CreateDataset(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_add_dataset.html'
    form_class = DatasetForm
    success_url = '/dataset-details/'

    @transaction.atomic
    def form_valid(self, form):
        dataset = form.save(commit=False)
        dataset.user = self.request.user
        dataset.save()

        self.success_url += str(dataset.id)
        return super(CreateDataset, self).form_valid(form)


class CreateSingleValue(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_add_single_value.html'
    form_class = SingleValueForm
    success_url = '/feature-details/'

    @transaction.atomic
    def form_valid(self, form):
        self.success_url += self.kwargs['model_object_id']

        prop = form.save(commit=False)
        prop.model_object_id = self.kwargs['model_object_id']
        prop.value_type = ValueType.objects.get(value_type='numerical')
        prop.save()
        value = NumValue(prop=prop, value=self.request.POST['value'])
        value.save()

        return super(CreateSingleValue, self).form_valid(form)


class CreateValueSeries(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_add_value_series.html'
    form_class = ValueSeriesForm
    success_url = '/feature-details/'

    @transaction.atomic
    def form_valid(self, form):
        self.success_url += self.kwargs['model_object_id']

        input_values = self.request.POST['values']
        prop = form.save(commit=False)
        prop.model_object_id = self.kwargs['model_object_id']
        prop.value_type = ValueType.objects.get(value_type='value_time_series')
        prop.interval = self.request.POST['interval']
        prop.timestart = self.request.POST['timestart']
        prop.num_vals = len(input_values.split(","))
        prop.save()

        value = ValueSeries(prop=prop, value='{'+input_values+'}')
        value.save()

        return super(CreateValueSeries, self).form_valid(form)

class CreateValueSeriesUpload(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_excel_upload.html'
    form_class = ValueSeriesUploadForm
    success_url = '/feature-details/'

    @transaction.atomic
    def form_valid(self, form):
        self.success_url += self.kwargs['model_object_id']

        files = self.get_form_kwargs().get('files').getlist('file_field')
        input_values = excel_handler(spreadsheet=files[0])

        prop = form.save(commit=False)
        prop.model_object_id = self.kwargs['model_object_id']
        prop.value_type = ValueType.objects.get(value_type='value_time_series')
        prop.interval = self.request.POST['interval']
        prop.timestart = self.request.POST['timestart']
        prop.num_vals = len(input_values)
        prop.save()

        value = ValueSeries(prop=prop, value=input_values)

        value.save()

        return super(CreateValueSeriesUpload, self).form_valid(form)




class CreateSingleRaster(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_add_single_raster.html'
    form_class = SingleRasterForm
    success_url = '/feature-details/'

    @transaction.atomic
    def form_valid(self, form):
        self.success_url += self.kwargs['model_object_id']

        prop = form.save(commit=False)
        prop.model_object_id = self.kwargs['model_object_id']
        prop.value_type = ValueType.objects.get(value_type='raster')
        prop.save()

        files = self.get_form_kwargs().get('files').getlist('file_field')
        raster = raster_handler(files)
        value = RasValue(prop=prop, value=raster)
        value.save()

        os.remove(raster.name)

        return super(CreateSingleRaster, self).form_valid(form)


class CreateRasterSeries(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_add_raster_series.html'
    form_class = RasterSeriesForm
    success_url = '/feature-details/'

    @transaction.atomic
    def form_valid(self, form):
        self.success_url += self.kwargs['model_object_id']

        files = self.get_form_kwargs().get('files').getlist('file_field')
        prop = form.save(commit=False)
        prop.model_object_id = self.kwargs['model_object_id']
        prop.value_type = ValueType.objects.get(value_type='raster_time_series')
        prop.interval = self.request.POST['interval']
        prop.timestart = self.request.POST['timestart']
        prop.num_vals = len(files)
        prop.save()

        raster = raster_handler(files)
        value = RasterSeries(prop=prop, value=raster)
        value.save()
        os.remove(raster.name)

        return super(CreateRasterSeries, self).form_valid(form)






def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/general/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def contact(request):
    """Renders the contact page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/general/contact.html',
        {
            'title':'Contact',
            'message':'Contact page.',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/general/about.html',
        {
            'title':'About',
            'message':'Some text will be here soon.',
            'year':datetime.now().year,
        }
    )
