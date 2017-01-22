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

        if not model_objects:
            return render(
                request, 'app/dataset_details.html',
                {'dataset': dataset, 'model_objects': model_objects,
                 'script': '<script></script>' ,
                 'objects_number': 0}
            )
        else:
            geojson = get_geojson(model_objects)
            script, div = plot_model_objects(
                geojson, map_width=500, map_height=500,
                table_width=550, table_height=550
                )

            return render(
                request, 'app/dataset_details.html',
                {'dataset': dataset, 'model_objects': model_objects,
                'script': script, 'plot': div['plot'], 'table': div['table'],
                'objects_number': len(model_objects)}
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
                request, 'app/model_object_details.html',
                {
                    'model_object': model_object, 'dataset': dataset, 'properties': properties,
                }
            )

        # if not properties:
        #     geojson = get_geojson([model_object])
        #     script, div = plot_model_objects(
        #         geojson, map_width=500, map_height=500,
        #         table_width=550, table_height=550
        #         )

        #     return render(
        #         request, 'app/model_object_details.html',
        #         {'model_object': model_object, 'dataset': dataset, 'properties': properties,
        #         'script': script, 'plot': div['plot'], 'table': div['table'],
        #         'properties_number': 0}
        #         )
        # else:
        #     geojson = get_prop_geojson(properties)
        #     script, div = plot_properties(
        #         geojson, map_width=500, map_height=500,
        #         table_width=550, table_height=550
        #         )

        #     return render(
        #         request, 'app/model_object_details.html',
        #         {'model_object': model_object, 'dataset': dataset, 'properties': properties,
        #          'script': script, 'plot': div['plot'], 'table': div['table'],
        #          'properties_number': len(properties)}
        #         )


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
            controls, raster_map, plot, table = div['controls'], div['raster_map'], div['plot'], None
            descr = 'time-series of rasters'
            value = None

        return render(
            request, 'app/property_details.html',
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
    template_name = 'app/create_model_object.html'
    form_class = ModelObjectForm
    success_url = '/dataset_details/'

    @transaction.atomic
    def form_valid(self, form):
        dataset_id = self.kwargs['dataset_id']
        self.success_url += dataset_id

        model_object = form.save(commit=False)
        model_object.dataset_id = dataset_id
        model_object.save()

        wkt = self.request.POST['wkt']
        bbox = set_geometry(
            geom_type=model_object.geom_type,
            model_object=model_object,
            geom_wkt=wkt)

        model_object.bbox = bbox
        model_object.save()

        dataset = Dataset.objects.get(id=dataset_id)
        if dataset.bbox is None:
            dataset.bbox = model_object.bbox
        else:
            dataset.bbox = update_bbox(bbox_geom=dataset.bbox,
                                       feature_geom=model_object.bbox)
        dataset.tile_url = calculate_tile_index(bbox_geom=dataset.bbox,
                                                as_url=True)
        dataset.save()

        return super(CreateModelObject, self).form_valid(form)

class CreateDataset(LoginRequiredMixin, CreateView):
    template_name = 'app/create_dataset.html'
    form_class = DatasetForm
    success_url = '/datacollections/'

    @transaction.atomic
    def form_valid(self, form):
        dataset = form.save(commit=False)
        dataset.user = self.request.user
        dataset.save()
        return super(CreateDataset, self).form_valid(form)


class PropertyForms(LoginRequiredMixin, TemplateView):
    template_name = 'app/property_forms.html'

    def get(self, request, *args, **kwargs):
        single_value_form = SingleValueForm(self.request.GET or None)
        value_series_form = ValueSeriesForm(self.request.GET or None)
        single_raster_form = SingleRasterForm(self.request.GET or None)
        raster_series_form = RasterSeriesForm(self.request.GET or None)
        context = self.get_context_data(**kwargs)
        context['model_object_id'] = self.kwargs['model_object_id']
        context['single_value_form'] = single_value_form
        context['value_series_form'] = value_series_form
        context['single_raster_form'] = single_raster_form
        context['raster_series_form'] = raster_series_form
        return self.render_to_response(context)


class CreateSingleValue(FormView):
    form_class = SingleValueForm
    template_name = 'app/property_forms.html'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        value_series_form = ValueSeriesForm()
        single_value_form = SingleValueForm(self.request.POST)
        single_raster_form = SingleRasterForm()
        raster_series_form = RasterSeriesForm()
    
        if single_value_form.is_valid():
            prop = single_value_form.save(commit=False)
            prop.model_object_id = self.kwargs['model_object_id']
            prop.value_type = ValueType.objects.get(value_type='numerical')
            prop.save()
            value = NumValue(prop=prop, value=self.request.POST['value'])
            value.save()
            return redirect(
                reverse('model_object_details', args=([int(self.kwargs['model_object_id'])])))

        else:
            return self.render_to_response(
                self.get_context_data(
                    value_series_form=value_series_form,
                    single_value_form=single_value_form,
                    single_raster_form=single_raster_form,
                    raster_series_form=raster_series_form,
                    model_object_id=self.kwargs['model_object_id']
                )
            )


class CreateValueSeries(FormView):
    form_class = ValueSeriesForm
    template_name = 'app/property_forms.html'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        value_series_form = ValueSeriesForm(self.request.POST)
        single_value_form = SingleValueForm()
        single_raster_form = SingleRasterForm()
        raster_series_form = RasterSeriesForm()

        if value_series_form.is_valid():
            input_values = self.request.POST['values']
            prop = value_series_form.save(commit=False)
            prop.model_object_id = self.kwargs['model_object_id']
            prop.value_type = ValueType.objects.get(value_type='value_time_series')
            prop.interval = self.request.POST['interval']
            prop.timestart = self.request.POST['timestart']
            prop.num_vals = len(input_values.split(","))
            prop.save()

            value = ValueSeries(prop=prop, value='{'+input_values+'}')
            value.save()
            return redirect(
                reverse('model_object_details', args=([int(self.kwargs['model_object_id'])])))

        else:
            return self.render_to_response(
                self.get_context_data(
                    value_series_form=value_series_form,
                    single_value_form=single_value_form,
                    single_raster_form=single_raster_form,
                    raster_series_form=raster_series_form,
                    model_object_id=self.kwargs['model_object_id']
                )
            )


class CreateSingleRaster(FormView):
    form_class = SingleRasterForm
    template_name = 'app/property_forms.html'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        value_series_form = ValueSeriesForm()
        single_value_form = SingleValueForm()
        single_raster_form = SingleRasterForm(self.request.POST, self.request.FILES)
        raster_series_form = RasterSeriesForm()

        if single_raster_form.is_valid():
            prop = single_raster_form.save(commit=False)
            prop.model_object_id = self.kwargs['model_object_id']
            prop.value_type = ValueType.objects.get(value_type='raster')
            prop.save()
            files = request.FILES.getlist('file_field')
            raster = raster_handler(files)
            value = RasValue(prop=prop, value=raster)
            value.save()
            return redirect(
                reverse('model_object_details', args=([int(self.kwargs['model_object_id'])])))

        else:
            return self.render_to_response(
                self.get_context_data(
                    value_series_form=value_series_form,
                    single_value_form=single_value_form,
                    single_raster_form=single_raster_form,
                    raster_series_form=raster_series_form,
                    model_object_id=self.kwargs['model_object_id']
                )
            )


class CreateRasterSeries(FormView):
    form_class = ValueSeriesForm
    template_name = 'app/property_forms.html'

    @transaction.atomic
    def post(self, request, *args, **kwargs):
        value_series_form = ValueSeriesForm()
        single_value_form = SingleValueForm()
        single_raster_form = SingleRasterForm()
        raster_series_form = RasterSeriesForm(self.request.POST, self.request.FILES)

        if raster_series_form.is_valid():
            files = request.FILES.getlist('file_field')
            prop = raster_series_form.save(commit=False)
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
            return redirect(
                reverse('model_object_details', args=([int(self.kwargs['model_object_id'])])))

        else:
            return self.render_to_response(
                self.get_context_data(
                    value_series_form=value_series_form,
                    single_value_form=single_value_form,
                    single_raster_form=single_raster_form,
                    raster_series_form=raster_series_form,
                    model_object_id=self.kwargs['model_object_id']
                )
            )






def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
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
        'app/contact.html',
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
        'app/about.html',
        {
            'title':'About',
            'message':'Some text will be here soon.',
            'year':datetime.now().year,
        }
    )
