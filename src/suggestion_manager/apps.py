from django.apps import AppConfig




class SuggestionManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'suggestion_manager'

    def ready(self) -> None:
        x = super().ready()
        from suggestion_manager.abstract_suggestion import AbstractSuggestion
        from suggestion_manager.suggestion_registry import SuggestionRegistry
        for i in AbstractSuggestion.__child_suggestions_to_register__:
            SuggestionRegistry(i)
        return x
