from django.contrib import admin
from django.apps import apps

models = apps.get_app_config("master").get_models()

for model in models:
    try:
        admin.site.register(model)
    except admin.sites.AlreadyRegistered:
        pass
