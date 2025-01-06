from model_utils.tracker import FieldTracker, FieldInstanceTracker

from .transaction_metadata import get_transaction_metadata


class Transactionsafe_FieldInstanceTracker(FieldInstanceTracker):
    """A field tracker that tracks changes within a transaction correctly.
    
    A call to changed_since_last_call_by(func) will return the old values of fields that have changed since the last call by the given function.
    
    Used to prevent discongruency between atomic and non-atomic calls.
    
    Exists because if an instance is changed and saved within the same transaction a signal that ought to 
    only fire on a change in X field may fire again if the change was in some other field Y because
    field X is still tracked as "changed" by the original field tracker implementation until the transaction complete/committed, 
    which leads to non-identical behaviour and circular calls if calls are atomic vs when they are non-atomic (not in a transaction).

    For example, if a signal is supposed to fire only when a field "mirror" is changed, and has already done so,
    but the signal also changes the field "last_updated" and saves the instance, 
    the signal while using the original changed function will fire again because 
    the original field tracker still considers "mirror" as changed despite the signal already having been fired for that change.
    Counterintuitively, if transactions are disabled, the signal will not fire again because the field tracker will 
    have already cleared "mirror" from the last call. Using this class and the changed_since_last_call_by method
    will prevent this behaviour by tracking the state at the last call by a specific function (signal) and 
    only returning the old values of fields that have changed since that call.
    """
    def __init__(self, instance, fields, field_map):
        super().__init__(instance, fields, field_map)

    def changed_since_last_call_by(self, func) -> dict:
        """Returns the old values of changed fields since the last call by a function (usually a signal) within this transaction.

        Only works if the instance already exists within the database, as it relies on the instance's primary key.

        Updates last call tracking for the given func. Ie, if called twice sequentially, second call will return an empty dict.
        
        Does not yet play nice with deffered fields. Exists to prevent double calling of signals since fieldtracker
          doesnt reset fields until transaction is complete"""

        if self.instance.pk is None:
            raise ValueError("Instance must have a primary key to track changes since the last call")

        made_calls = get_transaction_metadata("fieldtracker", {})
        identifier = self._func_object_id(func)

        #old values are the values at the last call
        old_values = made_calls.get(identifier, None)
        if old_values is None:
            old_values = {field: self.previous(field) for field in self.fields}
        current_values = self.current()

        changed_fields = [field for field in self.fields if old_values.get(field, None) != current_values.get(field)]
        changed_dict = {key: old_values[key] for key in changed_fields if key in old_values.keys()}
        made_calls[identifier] = current_values
        return changed_dict

    def get_previous_state_since_last_call_by(self, func) -> dict:
        """Returns the old values of all fields since the last call by a function (usually a signal) within this transaction.

        Only works if the instance already exists within the database, as it relies on the instance's primary key.

        Updates last call tracking for the given func. Ie, if called twice sequentially, second call will return the current values.
        
        Does not yet play nice with deffered fields. Exists to prevent double calling of signals since fieldtracker
          doesnt reset fields until transaction is complete"""

        if self.instance.pk is None:
            raise ValueError("Instance must have a primary key to track changes since the last call")

        made_calls = get_transaction_metadata("fieldtracker", {})
        identifier = self._func_object_id(func)

        old_values = made_calls.get(identifier, {})
        made_calls[identifier] = self.current()
        return old_values

    def _func_object_id(self, func):
        return f"{func.__module__}.{func.__name__}" + str(self.instance.pk)

class TransactionsafeFieldTracker(FieldTracker):
    tracker_class = Transactionsafe_FieldInstanceTracker
    def __init__(self, fields = None):
        super().__init__(fields)




