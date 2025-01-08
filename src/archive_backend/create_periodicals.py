from django_q.models import Schedule
from django.core.exceptions import ObjectDoesNotExist

from archive_backend.api.download_all import update_download_all
from archive_backend.models import RemotePeer



def check_scheduled_task(task_name, actual_func, default_schedule_type = "D", *args, **kwargs):
    """Checks if a scheduled task exists, and if not, creates it with the default schedule type.
    
    @param task_name: The name of the scheduled task in the overview.
    @param callsign: The function callsign to call.
    @param default_schedule_type: The default schedule type to use if the task does not exist. (Daily if not given).
    @param *args, **kwargs: The arguments to pass to the function.
    """
    try:
        Schedule.objects.get(name=task_name)
        return
    except ObjectDoesNotExist:
        callsign = actual_func.__module__ + "." + actual_func.__name__
        Schedule(name=task_name, 
                 func=callsign, 
                 schedule_type=default_schedule_type,
                 repeats = -1, 
                 args = args, 
                 kwargs = kwargs).save()
        

def update_from_remotes():
    for peer in RemotePeer.objects.exclude(is_this_site = True).filter(mirror_files = True):
        update_download_all(peer)

def setup_scheduled_tasks():
    check_scheduled_task("Update from remotes", update_from_remotes)