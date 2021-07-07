#!/bin/sh
set -e
. ./venv/bin/activate
. ./secrets.env
exec python -m balthify
