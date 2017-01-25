"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.forms import SimpleArrayField
# from django.contrib.gis import forms

from app.models import *

class BootstrapAuthenticationForm(AuthenticationForm):
    """Authentication form which uses boostrap CSS."""
    username = forms.CharField(max_length=254,
                               widget=forms.TextInput({
                                   'class': 'form-control',
                                   'placeholder': 'User name'}))
    password = forms.CharField(label=_("Password"),
                               widget=forms.PasswordInput({
                                   'class': 'form-control',
                                   'placeholder':'Password'}))




class DatasetForm(forms.ModelForm):

    class Meta:
        model = Dataset
        fields = ['public', 'name', 'descr']


class ModelObjectForm(forms.ModelForm):
    geometry = forms.CharField(
        widget=forms.Textarea(
            attrs={
            'placeholder': 'WKT formatted geometry in EPSG:3857 CRS. \n\
Examples:\n\
point(0 0),\n\
linestring(0 0, 1 1, 2 2,)\n\
polygon((0 0, 1 1, 2 2, 0 0))'
            }
        ),
        required=False
    )
    class Meta:
        model = ModelObject
        fields = ['object_type', 'name']


class SingleValueForm(forms.ModelForm):
    value = forms.FloatField()
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

class ValueSeriesForm(forms.ModelForm):
    timestart = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'placeholder':'2017-01-01 00:00:00'
                }
            )
        )
    interval = forms.DurationField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'00:00:00'
                }
            )
        )
    values = SimpleArrayField(forms.DecimalField(),
        widget=forms.TextInput(
            attrs={
                'placeholder':'1, 1, 2, 3, etc.'
                }
            )
        )
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

class ValueSeriesUploadForm(forms.ModelForm):
    timestart = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'placeholder':'2017-01-01 00:00:00'
                }
            )
        )
    interval = forms.DurationField(
        widget=forms.TextInput(
            attrs={
                'placeholder':'00:00:00'
                }
            )
        )
    file_field = forms.FileField()
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

class SingleRasterForm(forms.ModelForm):
    file_field = forms.FileField()
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

class RasterSeriesForm(forms.ModelForm):
    timestart = forms.DateTimeField()
    interval =forms.DurationField()
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

