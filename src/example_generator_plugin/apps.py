from django.apps import AppConfig


class ExampleGeneratorPluginConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'example_generator_plugin'

    def ready(self):
        from archive_backend.generation import generators
        from .example_generator import text_all_caps
        generators.register("example_generator_plugin.txt_to_caps", text_all_caps)
