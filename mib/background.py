from mib import create_app, create_celery # pragma: no cover

flask_app = create_app() # pragma: no cover
app = create_celery(flask_app) # pragma: no cover
