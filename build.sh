#!/usr/bin/env bash

# Exist on error
set -o errexit

# Modify this line as needed for package manager
pip install -r requiremenets.txt


# Apply any outstanding database migrations
python manage.py migrate

