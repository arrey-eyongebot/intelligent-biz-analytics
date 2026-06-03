#!/bin/sh
exec gunicorn --bind 0.0.0.0:$PORT --workers 2 --chdir backend app:app
