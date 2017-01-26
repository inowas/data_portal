from django.core.exceptions import ValidationError
import os

def valid_geometry_file(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.geojson']
    if not ext in valid_extensions:
        raise ValidationError('File not supported!')

def valid_spreadsheet_file(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.xls', '.xlsx']
    if not ext in valid_extensions:
        raise ValidationError('File not supported!')

def valid_raster_file(value):
    ext = os.path.splitext(value.name)[1]
    valid_extensions = ['.tif', '.png']
    if not ext in valid_extensions:
        raise ValidationError('File not supported!')
