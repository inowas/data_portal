#!/usr/bin/env bash

python manage.py loaddata ./app/fixtures/feature_types.json
python manage.py loaddata ./app/fixtures/geom_types.json
python manage.py loaddata ./app/fixtures/property_types.json
python manage.py loaddata ./app/fixtures/value_types.json
