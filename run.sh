#!/bin/sh
set -e
cd "$(dirname $0)"
. ./venv/bin/activate
. ./secrets.env
exec python -m balthify
