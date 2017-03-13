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
from django.core.exceptions import PermissionDenied
from django.db import transaction
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.gis.geos import GEOSGeometry

from app.models import *
from app.forms import *
from app.utils import *
from app.vis.bokeh_plots import *
from app.permissions import *
from django.views.decorators.csrf import csrf_protect, ensure_csrf_cookie   

from datetime import timedelta 


@csrf_protect
@ensure_csrf_cookie
def toolbox(request):
    return render(request, 'tools_angular/index.html')

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

        if dataset.public == False and dataset.user != self.request.user:
            raise PermissionDenied

        model_objects = ModelObject.objects.filter(dataset=dataset)

        return render(
            request, 'app/details_dataset.html',
            {
                'dataset': dataset,
                'model_objects': model_objects,
                'geojson_url': '/api/geojson-dataset/' + str(dataset.id),
                'view': 'dataset_details'
            }
        )

class ModelObjectDetails(View):

    def get(self, request, model_object_id):
        try:
            model_object = ModelObject.objects.get(id=model_object_id)
        except ModelObject.DoesNotExist:
            raise Http404("Object does not exist")
        dataset = Dataset.objects.get(id=model_object.dataset_id)

        if dataset.public == False and dataset.user != self.request.user:
            raise PermissionDenied

        properties = Prop.objects.filter(model_object=model_object)

        return render(
            request, 'app/details_feature.html',
            {
                'dataset': dataset,
                'model_object': model_object,
                'properties': properties,
                'geojson_url': '/api/geojson-feature/' + str(model_object.id),
                'view': 'feature_details'
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

        if dataset.public == False and dataset.user != self.request.user:
            raise PermissionDenied

        if prop.value_type.value_type == 'numerical':
            try:
                value = NumValue.objects.get(prop=prop)
            except NumValue.DoesNotExist:
                raise Http404("Property has no values")

            controls, raster_map, plot, table, script = None, None, None, None, None
            descr = 'single numerical value'
            value = str(value.value)
            value_type = 'numerical'
            time_start = None
            time_end = None
            num_vals = None

        elif prop.value_type.value_type == 'categorical':
            try:
                value = CatValue.objects.get(prop=prop)
            except CatValue.DoesNotExist:
                raise Http404("Property has no values")
            controls, raster_map, plot, table, script = None, None, None, None, None
            descr = 'single numerical value'
            value = str(value.value)
            value_type = 'categorical'
            time_start = None
            time_end = None
            num_vals = None

        elif prop.value_type.value_type == 'value_time_series':
            try:
                value = ValueSeries.objects.get(prop=prop)
            except ValueSeries.DoesNotExist:
                raise Http404("Property has no values")

            script, div = plot_time_series(
                values=value.value, timestamps=value.timestamps,
                plot_width=700, plot_height=500,
                table_width=550, table_height=550
                )

            controls, raster_map, plot, table = None, None, div['plot'], div['table']
            descr = 'time-series of values'
            value_type = 'value_time_series'
            time_start = value.timestamps[0]
            time_end = value.timestamps[-1]
            num_vals = len(value.timestamps)
            value = None

        elif prop.value_type.value_type == 'raster':
            try:
                raster = RasValue.objects.get(prop=prop)
            except RasValue.DoesNotExist:
                raise Http404("Property has no values")

            script, div = plot_single_raster(
                raster, resize_coef=1., plot_width=600, plot_height=400,
                table_width=550, table_height=550
                )
            controls, raster_map, plot, table = None, div['raster_map'], div['plot'], None
            descr = 'singe raster'
            value = None
            value_type = 'raster'
            time_start = None
            time_end = None
            num_vals = None

        elif prop.value_type.value_type == 'raster_time_series':
            try:
                raster = RasterSeries.objects.get(prop=prop)
            except RasterSeries.DoesNotExist:
                raise Http404("Property does not exist")

            script, div = plot_raster_series(
                raster=raster.value, timestamps=raster.timestamps,
                resize_coef=0.1, plot_width=600, plot_height=400
                )
            controls, raster_map, plot, table = div['controls'],\
            div['raster_map'], div['plot'], None

            descr = 'time-series of rasters'
            value = None
            value_type = 'raster_time_series'
            time_start = raster.timestamps[0]
            time_end = raster.timestamps[-1]
            num_vals = len(raster.timestamps)

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
                'prop': prop,
                'value_type': value_type,
                'time_start': time_start,
                'time_end': time_end,
                'num_vals': num_vals,
                'view': 'property_details'
                }
            )


class CreateModelObject(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_add_feature.html'
    form_class = ModelObjectForm
    success_url = '/dataset-details/'

    def get_context_data(self, **kwargs):
        context = super(CreateModelObject, self).get_context_data(**kwargs)
        dataset_id = self.kwargs['dataset_id']
        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            raise Http404("Dataset does not exist")

        if dataset.user != self.request.user:
            raise PermissionDenied

        context['form'].fields['sampled_feature'].queryset = ModelObject.objects.filter(
            dataset_id=self.kwargs['dataset_id']
            )
        return context

    @transaction.atomic
    def form_valid(self, form):
        dataset_id = self.kwargs['dataset_id']

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            raise Http404("Dataset does not exist")

        if dataset.user != self.request.user:
            raise PermissionDenied

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

        update_bbox(dataset_id)

        return super(CreateModelObject, self).form_valid(form)


class CreateModelObjectsUpload(LoginRequiredMixin, FormView):
    template_name = 'app/create_forms/form_template_geojson_upload.html'
    form_class = ModelObjectUploadForm
    success_url = '/dataset-details/'

    @transaction.atomic
    def form_valid(self, form):

        dataset_id = self.kwargs['dataset_id']

        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            raise Http404("Dataset does not exist")

        if dataset.user != self.request.user:
            raise PermissionDenied

        try:

            self.success_url += dataset_id

            files = self.get_form_kwargs().get('files').getlist('file_field')
            features, names, types, sampled_features = shape_handler(files[0])
            for f, n, t, s in zip(features, names, types, sampled_features):
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
                    geom_type_id=geom_type_id,
                    sampled_feature=ModelObject.objects.filter(name=s)[0] if s else None
                )

                model_object.save()

            update_bbox(dataset_id)

        except:
            return render(
                self.request,
                self.template_name,
                {'form': form,
                 'error_message': 'INVALID INPUT!'}
            )

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
        try:
            self.success_url += self.kwargs['model_object_id']

            input_values = self.request.POST['values']
            input_timestamps = self.request.POST['timestamps']

            prop = form.save(commit=False)
            prop.model_object_id = self.kwargs['model_object_id']
            prop.value_type = ValueType.objects.get(value_type='value_time_series')
            prop.save()

            values = [i.strip() for i in input_values.split(',')]
            timestamps = [i.strip() for i in input_timestamps.split(',')]

            if len(values) != len(timestamps):
                raise ValidationError("Not equal series")

            value = ValueSeries(
                prop=prop,
                value=values,
                timestamps=timestamps
                )
            value.save()

        except ValidationError:

            return render(
                self.request,
                self.template_name,
                {'form': form,
                 'error_message': 'INVALID INPUT!'}
            )


        return super(CreateValueSeries, self).form_valid(form)

class CreateValueSeriesUpload(LoginRequiredMixin, CreateView):
    template_name = 'app/create_forms/form_template_excel_upload.html'
    form_class = ValueSeriesUploadForm
    success_url = '/feature-details/'

    @transaction.atomic
    def form_valid(self, form):
        try:
            self.success_url += self.kwargs['model_object_id']

            files = self.get_form_kwargs().get('files').getlist('file_field')
            values, timestamps = excel_handler(spreadsheet=files[0])

            prop = form.save(commit=False)
            prop.model_object_id = self.kwargs['model_object_id']
            prop.value_type = ValueType.objects.get(value_type='value_time_series')

            prop.save()

            if len(values) != len(timestamps):
                raise ValidationError("Not equal series")

            value = ValueSeries(
                prop=prop,
                value=values,
                timestamps=timestamps)

            value.save()

        except:
            return render(
                self.request,
                self.template_name,
                {'form': form,
                 'error_message': 'INVALID INPUT!'}
            )


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
        try:
            self.success_url += self.kwargs['model_object_id']

            files = self.get_form_kwargs().get('files').getlist('file_field')
            input_timestamps = self.request.POST['timestamps']
            timestamps = [i.strip() for i in input_timestamps.split(',')]
            if len(files) != len(timestamps):
                raise ValidationError("Not equal series")

            prop = form.save(commit=False)
            prop.model_object_id = self.kwargs['model_object_id']
            prop.value_type = ValueType.objects.get(value_type='raster_time_series')
            prop.save()

            raster = raster_handler(files)

            value = RasterSeries(
                prop=prop,
                value=raster,
                timestamps=timestamps
                )
            value.save()
            os.remove(raster.name)

        except ValidationError:
            return render(
                self.request,
                self.template_name,
                {'form': form,
                 'error_message': 'INVALID INPUT!'}
            )


        return super(CreateRasterSeries, self).form_valid(form)


class UpdateDataset(LoginRequiredMixin, FormView):

    template_name = 'app/create_forms/form_template_update_dataset.html'
    form_class = DatasetForm
    success_url = '/dataset-details/'

    def get_context_data(self, **kwargs):

        context = super(UpdateDataset, self).get_context_data(**kwargs)
        dataset_id = self.kwargs['dataset_id']
        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            raise Http404("Dataset does not exist")

        if dataset.user != self.request.user:
            raise PermissionDenied

        context['dataset'] = dataset
        context['form'].fields['name'].initial = dataset.name
        # context['form'].fields['tags'].initial = str(dataset.tags)
        context['form'].fields['descr'].initial = dataset.descr

        return context

    @transaction.atomic
    def form_valid(self, form):

        dataset_id = self.kwargs['dataset_id']
        try:
            dataset = Dataset.objects.get(id=dataset_id)
        except Dataset.DoesNotExist:
            raise Http404("Dataset does not exist")

        if dataset.user != self.request.user:
            raise PermissionDenied

        dataset.name = self.request.POST['name']
        dataset.descr = self.request.POST['descr']
        # print(self.request.POST['public'])
        public = self.request.POST.get('public', False)
        if public == 'on':
            dataset.public = True
        else:
            dataset.public = False
        # dataset.tags = self.request.POST['tags']

        dataset.save()

        self.success_url += str(dataset_id)
        return super(UpdateDataset, self).form_valid(form)



def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return redirect('explorer')
    # return render(
    #     request,
    #     'app/general/index.html',
    #     {
    #         'title':'Home Page',
    #         'year':datetime.now().year,
    #     }
    # )

# def contact(request):
#     """Renders the contact page."""
#     assert isinstance(request, HttpRequest)
#     return render(
#         request,
#         'app/general/contact.html',
#         {
#             'title':'Contact',
#             'message':'Contact page.',
#             'year':datetime.now().year,
#         }
#     )

# def about(request):
#     """Renders the about page."""
#     assert isinstance(request, HttpRequest)
#     return render(
#         request,
#         'app/general/about.html',
#         {
#             'title':'About',
#             'message':'Some text will be here soon.',
#             'year':datetime.now().year,
#         }
#     )

def impressum(request):
    """Renders the about page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/general/impressum.html',
        {
            'title':'Impressum',
            'year':datetime.now().year,
        }
    )
