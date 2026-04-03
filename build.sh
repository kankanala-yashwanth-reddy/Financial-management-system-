#!/bin/bash
set -o errexit

# Ensure setuptools is installed to avoid pkg_resources error
pip install --upgrade pip setuptools
pip install -r requirements.txt
