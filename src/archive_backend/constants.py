from django.apps import apps


maxFileNameLength = 500
descriptionLength = 500
authorLength = 100
titleLength = 200
api_subpath = "api/"


archiveAppConfig = apps.get_app_config("archive_backend")