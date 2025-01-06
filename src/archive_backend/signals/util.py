from typing import List, Set
from archive_backend.utils import get_transaction_metadata


def post_save_old_values(**signalkwargs):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will not fire on new instances. Relies on the FieldTracker utility from model_utils being called field_tracker in the model.

    The old values of the instance must be equal to the kwargs dictionary. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            if created:
                return #New items cant have old values
            
            for key, value in signalkwargs.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                oldValue = instance.field_tracker.previous(key)
                if value != oldValue:
                    return
            return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner

def post_save_new_values(**signalkwargs):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    The new values of the instance must be equal to the kwargs dictionary. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            for key, value in signalkwargs.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                newValue = getattr(instance, key)
                if value != newValue:
                    return
            return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner

def post_save_new_values_NOTEQUALS_OR(**signalkwargs):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    None of the new values of the instance must be equal to the criteria in the kwargs dictionary, 
    meaning that if one equality matches, the signal wont fire. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            for key, value in signalkwargs.items():
                if not hasattr(instance, key):
                    raise Exception("Attribute " + key + " does not exist")
                newValue = getattr(instance, key)
                if value == newValue:
                    return
            return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner


""" Following code exists because if an instance is changed and saved within the same transaction a signal that ought to 
    only fire on a change in X field may fire again if the change was in some other field Y because
    field X is still tracked as "changed" by the field tracker until the transaction complete/committed, 
    which leads to non-identical behaviour and circular calls if calls are atomic vs when they are non-atomic (not in a transaction).
    
    This not-so-perfect patch stores the previous relevant new state of the object any time the signal is called."""

def signal_object_id(func, object_id):
    """Utility function to generate a unique identifier for a signal call with a specific object.
    
    Exists because if an instance is changed and saved within the same transaction a signal that ought to 
    only fire on a change in X field may fire again if the change was in some other field Y because
    field X is still tracked as "changed" by the field tracker until the transaction complete/committed, 
    which leads to non-identical behaviour and circular calls if calls are atomic vs when they are non-atomic (not in a transaction)."""
    return f"{func.__module__}.{func.__name__}" + str(object_id)

def store_previous_call_and_state(func, instance, fields):
    """Utility function to store the signal call in the transaction metadata.
    
    Exists because if an instance is changed and saved within the same transaction, a signal that ought to 
    only fire on a change in X field may fire again if the change was in some other field Y because
    field X is still tracked as "changed" by the field tracker until the transaction complete/committed, 
    which leads to non-identical behaviour and circular calls if calls are atomic vs when they are non-atomic (not in a transaction).
    
    @param: Decorated signal function that was called.
    @param: Instance on which the signal is called.
    @fields: Fields on which change is tested"""
    made_calls = get_transaction_metadata("signal", {})
    signal_object_id = signal_object_id(func, instance.pk)
    filtered_current_values = {key: getattr(instance, key) for key in fields}
    made_calls[signal_object_id] = filtered_current_values

def last_call_identical(func, instance, fields):
    """Utility function to check if the last call to a signal in this transition was identical to the current one.

    Exists because if an instance is changed and saved within the same transaction a signal that ought to 
    only fire on a change in X field may fire again if the change was in some other field Y because
    field X is still tracked as "changed" by the field tracker until the transaction complete/committed, 
    which leads to non-identical behaviour and circular calls if calls are atomic vs when they are non-atomic (not in a transaction).
    
    @param: Decorated signal function that was called.
    @param: Instance on which the signal is called.
    @fields: Fields on which change is tested"""
    made_calls = get_transaction_metadata("signal", {})
    signal_object_id = signal_object_id(func, instance.pk)
    last_call = made_calls.get(signal_object_id, None)
    if last_call is None:
        return False
    filtered_current_values = {key: getattr(instance, key) for key in fields}
    return last_call == filtered_current_values

def last_call_fully_different(func, instance, fields):
    """Utility function to check if the last call to a signal in this transition has fields that are fully different to the last state it was called with.


    
    @param: Decorated signal function that was called.
    @param: Instance on which the signal is called.
    @fields: Fields on which change is tested"""
    made_calls = get_transaction_metadata("signal", {})
    signal_object_id = signal_object_id(func, instance.pk)
    last_call = made_calls.get(signal_object_id, None)
    if last_call is None:
        return True
    for key in fields:
        if getattr(instance, key) == last_call[key]:
            return False
    return True

def post_save_change_in_values(*valuesMustHaveChanged):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will not fire signal on new items.

    The values of the instance must have changed in the new data content. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            changes = instance.field_tracker.changed()
            if len(changes) == 0:
                return #No changes
            for key in valuesMustHaveChanged:
                if key not in changes.keys():
                    return #Key not changed
                
            #See comments in last_call functions for explaination
            if last_call_fully_different(func, instance, valuesMustHaveChanged):
                store_previous_call_and_state(func, instance, valuesMustHaveChanged)
                return func(sender, instance, created, *args, **kwargs)
            #Store last call regardless, as the true (relevant) previous state needs to be known.
            store_previous_call_and_state(func, instance, valuesMustHaveChanged)
            return
        return internal_filter
    return inner

def post_save_change_in_any(*valuesMustHaveChanged):
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will not fire signal on new items.

    One of the given values of the instance must have changed in the new data content. (reference equality)"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            changes = instance.field_tracker.changed()
            if len(changes) == 0:
                return #No changes
            has_changes = False
            for key in valuesMustHaveChanged:
                if key in changes.keys():
                    has_changes = True
            if has_changes:
                #See comments in last_call functions for explaination
                if not last_call_identical(func, instance, valuesMustHaveChanged):
                    store_previous_call_and_state(func, instance, valuesMustHaveChanged)
                    return func(sender, instance, created, *args, **kwargs)
                #Save the last call regardless because its true state is relevant
                store_previous_call_and_state(func, instance, valuesMustHaveChanged)
                return #last call in this transaction was identical
            return
        return internal_filter
    return inner

def post_save_new_item():
    """Utility function to stop firing a post_save signal if the model instance does not meet the criteria.

    Will only fire signal on new items."""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            if created:
                return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner

def post_save_is_local_model(bool):
    """Only run the signal on local models, or only on remote models if set to False"""
    def inner(func):
        def internal_filter(sender = None, instance = None, created = None, *args, **kwargs):
            if instance.from_remote.is_this_site == bool:
                return func(sender, instance, created, *args, **kwargs)
        return internal_filter
    return inner