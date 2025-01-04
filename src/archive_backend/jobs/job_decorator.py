
from datetime import datetime, timedelta
from archive_backend import config
from django_q.tasks import async_task, schedule

from archive_backend.jobs.job_exceptions import BaseJobRescheduleException
from archive_backend.models.util_abstract_models.remote_model import RemoteModel
from typing import Type


identity = (lambda x: x, lambda x: x)

def get_remote_model_serializer_pair(model: Type[RemoteModel]):
    serializer = lambda model_instance: str(model_instance.id)
    deserializer = lambda val: model.objects.get(id = val)
    return (serializer, deserializer)

def jobify(func_callsign, *arg_transformers, **kwarg_transformers):
    """Transforms a function call into a queued job call.

    If global config.do_job_queueing is set to False (use --nojobqueing on runbackend command), or decorated function is called with force_call_synchronously=True, the function will work as if decorator does not exist (no use of djang-q, no catching of BaseJobRescheduleExceptions).

    If

    Will automatically reschedule itself if a BaseJobRescheduleException was raised is job queueing is enabled.

    Use the provided identity function for a serializer/deserializer if the argument is already a primitive.

    Function can be called as if unmodified.
    
    :param func_callsign: The dotted callsign of the function to be called.
    :param arg_transformers: A list of tuples of the form (serializer, deserializer) for each argument, such that they can be saved as primitives in the db.
    :param kwarg_transformers: A dictionary of the form {kwarg_name: (serializer, deserializer)} for each kwarg, such that they can be saved as primitives in the db."""
    def decorator(func):
        def wrapper(*args, called_by_queue_handler=False, force_call_synchronously = False, **kwargs):
            #If queueing is disabled, or force_call_synchronously is True, execute directly with no catching and no queueing
            #If "called_by_queue_handler" = True, it is called by queue handler, deserializes args and kwargs and runs the original function
            #If "called_by_queue_handler" = False, it is called normally, which then schedules a task for this function with its args serialized
            if not config.do_job_queueing or force_call_synchronously:
                print("Debug job: Calling " + func_callsign + " synchronously")
                func(*args, **kwargs)
                return
            if called_by_queue_handler:
                #args and kwargs given are in serialized form, so we deserialize them
                actual_args = [arg_transformer[1](arg) for arg, arg_transformer in zip(args, arg_transformers)]
                actual_kwargs = {key: kwarg_transformers[key][1](value) if key in kwarg_transformers else value for key, value in kwargs.items()}
                try:
                    #try catch here ensures that reschedule exceptions (such as the remote host not responding, or a remote job not being finished) 
                    # do not cause job failure, but reschedule the job for n minutes
                    func(*actual_args, **actual_kwargs)
                except BaseJobRescheduleException as e:
                    #schedule function (in the form by queue handler, so it will immediately execute, not schedule another job) 
                    # again with already serialized args and kwargs after delay of minutes defined in exception
                    schedule(func_callsign, *args, called_by_queue_handler = True, **kwargs, 
                             name="Rescheduled " + func_callsign, schedule_type="O", 
                             next_run = datetime.now() + timedelta(minutes=e.delay_in_minutes))
                return
            else:
                #args and kwargs are in real python form, so we serialize them
                serialized_args = [arg_transformer[0](arg) for arg, arg_transformer in zip(args, arg_transformers)]
                serialized_kwargs = {key: kwarg_transformers[key][0](value) if key in kwarg_transformers else value for key, value in kwargs.items()}
                serialized_kwargs['called_by_queue_handler'] = True
                async_task(func_callsign, *serialized_args, **serialized_kwargs, task_name=func_callsign)
                return
        return wrapper
    return decorator


def jobify_model(func_callsign: str, model: Type[RemoteModel]):
    """Transforms a function call into a queued job call, with the decorated functions first and only argument being a remote model instance.

    If global config.do_job_queueing is set to False (use --nojobqueing on runbackend command), function will work as if decorator does not exist (and will not catch BaseJobRescheduleExceptions).

    Will automatically reschedule itself if a BaseJobRescheduleException was raised is job queueing is enabled.

    Function can be called as if unmodified.
    
    :param func_callsign: The dotted callsign of the function to be called.
    :param model: The model class to be used for serialization/deserialization.
    """
    def decorator(func):
        return jobify(func_callsign, get_remote_model_serializer_pair(model))(func)
    return decorator
