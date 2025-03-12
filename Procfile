web: gunicorn JobBoard.wsgi --log-file -
worker: celery -A JobBoard worker --loglevel=info