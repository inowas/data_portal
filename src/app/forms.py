"""
Definition of forms.
"""

from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.utils.translation import ugettext_lazy as _
from django.contrib.postgres.forms import SimpleArrayField

from app.validators import *
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
                'placeholder': 'point(0 0), ' +
                               'linestring(0 0, 1 1, 2 2,), ' +
                               'polygon((0 0, 1 1, 2 2, 0 0))'
            }
        ),
        required=False
    )

    class Meta:
        model = ModelObject
        fields = ['name', 'object_type', 'sampled_feature']


class ModelObjectUploadForm(forms.Form):
    file_field = forms.FileField(validators=[valid_geometry_file])


class SingleValueForm(forms.ModelForm):
    value = forms.FloatField()
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

class ValueSeriesForm(forms.ModelForm):
    timestamps = SimpleArrayField(
        forms.DateTimeField(),
        widget=forms.DateTimeInput(
            attrs={
                'placeholder':'2017-01-01 00:00:00, 2017-01-02 00:00:00, etc.'
                }
            )
        )

    values = SimpleArrayField(
        forms.DecimalField(),
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
    file_field = forms.FileField(validators=[valid_spreadsheet_file])
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

class SingleRasterForm(forms.ModelForm):
    file_field = forms.FileField()
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

class RasterSeriesForm(forms.ModelForm):
    timestamps = SimpleArrayField(
        forms.DateTimeField(),
        widget=forms.DateTimeInput(
            attrs={
                'placeholder':'2017-01-01 00:00:00, 2017-01-02 00:00:00, etc.'
                }
            )
        )
    file_field = forms.FileField(widget=forms.ClearableFileInput(attrs={'multiple': True}))
    class Meta:
        model = Prop
        fields = ['property_type', 'name']

