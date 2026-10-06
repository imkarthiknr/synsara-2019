#!/bin/sh
# Apply database migrations, then start the app.
set -e
alembic upgrade head
exec "$@"
