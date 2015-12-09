web: gunicorn Drinklet.wsgi --log-file -
worker: celery worker --app=tasks.app
