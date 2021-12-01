# pragma: no cover
from mib import create_app, create_celery

flask_app = create_app()
app = create_celery(flask_app)
