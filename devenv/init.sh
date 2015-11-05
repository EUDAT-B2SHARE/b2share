#!/bin/sh

python manage.py db init
python manage.py db create

cat <<END_INSTRUCTIONS

# Now you can run in two different terminals
$ celery worker -A b2share.celery -l INFO --workdir=$VIRTUAL_ENV
# and
$ python manage.py run

END_INSTRUCTIONS
