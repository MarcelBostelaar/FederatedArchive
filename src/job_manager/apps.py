from django.apps import AppConfig



class JobManagerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'job_manager'

    def ready(self) -> None:
        x = super().ready()
        from job_manager.abstract_job import AbstractJob
        from job_manager.jobs_registry import JobsRegistry
        for i in AbstractJob.__child_jobs_to_register__:
            JobsRegistry(i)
        return x
