web: gunicorn Drinklet.wsgi --log-file -
worker: celery worker -A Drinklet --without-gossip --without-mingle --without-heartbeat
