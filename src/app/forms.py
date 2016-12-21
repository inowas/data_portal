"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.forms import SimpleArrayField

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
    wkt = forms.CharField(widget=forms.Textarea, required=False)
    class Meta:
        model = ModelObject
        fields = ['dataset', 'geom_type', 'object_type', 'wkt']


class SingleValueForm(forms.ModelForm):
    value = forms.FloatField()
    class Meta:
        model = Prop
        fields = ['property_type', 'obs_point']

class ValueSeriesForm(forms.ModelForm):
    timestart = forms.DateTimeField()
    interval =forms.DurationField()
    values = SimpleArrayField(forms.DecimalField())
    class Meta:
        model = Prop
        fields = ['property_type', 'obs_point']

class SingleRasterForm(forms.ModelForm):
    file_field = forms.FileField()
    class Meta:
        model = Prop
        fields = ['property_type', 'obs_point']

class RasterSeriesForm(forms.ModelForm):
    timestart = forms.DateTimeField()
    interval =forms.DurationField()
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = Prop
        fields = ['property_type', 'obs_point']

