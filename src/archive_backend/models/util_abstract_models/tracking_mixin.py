from typing import List

class ModelDelta:
    """A class representing the difference between two states of an instance of a model."""
    def __init__(self, old_state: dict, new_state: dict):
        self.old_state = old_state
        self.new_state = new_state

    def get_changed_fields(self) -> List[str]:
        """Returns a list of the fields that have changed."""
        return [key for key in self.old_state.keys() if self.old_state[key] != self.new_state[key]]

    def get_diff_old(self) -> dict:
        """Returns the old values of only the fields that have changed."""
        return {key: self.old_state[key] for key in self.old_state.keys() if self.old_state[key] != self.new_state[key]}
    
    def get_diff_new(self) -> dict:
        """Returns the new values of only the fields that have changed."""
        return {key: self.new_state[key] for key in self.new_state.keys() if self.old_state[key] != self.new_state[key]}

class TrackingMixin:
    """Tracks all fields of a django model it is added to during its lifecycle in the django codebase.
    Must be used as a mixin with a django model class."""

    def get_tracked_fields(self):
        """Override to limit the fields to track"""
        return self._meta.fields

    def _get_current_values(self):
        """Returns the current values of all fields in the instance as a storable dict."""
        return {field.attname: getattr(self, field.attname) for field in self.get_tracked_fields()}

    def trigger_tracking_for_id(self, identifier) -> ModelDelta:
        """Returns the difference between the previous and current state and sets the previous state to the current state for the next track cycle.

        Usefull for tracking changes between two points in time, which can be helpfull in signals to prevent unneccecary firing or to get the pre-save values.
        Use any hashable identifier (such as a signal func) to track changes between two points in time for a specific purpose.
        
        @param the tracking id. Use any hashable identifier (such as a signal func) to track changes between two points in time of calling with this id.
        @returns ModelDelta object representing the difference between the state at the previous call (or init) and new state of the instance during its lifetime on this server. """
        if identifier is None:
            raise ValueError("Identifier must not be None, as this is used to track general state between saves.")
        return self._trigger_tracking_for_id(identifier)

    def _trigger_tracking_for_id(self, identifier = None) -> ModelDelta:
        """Resets tracking point. Internal use only, does allow None identifier."""
        old_state = self._state_store.get(identifier, self._initial_state)
        new_state = self._get_current_values()
        self._state_store[identifier] = new_state
        return ModelDelta(old_state, new_state)

    def previous(self, field, identifier = None) -> any:
        """Returns the previous field value of the model instance for the given identifier. If no identifier is given, returns the state at the previous save (or init)."""
        return self._state_store.get(identifier, self._initial_state)[field]
    
    def previous_state(self, identifier = None) -> dict:
        """Returns the previous state of the model instance for the given identifier. If no identifier is given, returns the state at the previous save (or init)."""
        return self._state_store.get(identifier, self._initial_state)



    #post init trickery from https://stackoverflow.com/a/72593763/7183662
    def __init_subclass__(cls, **kwargs):
        """Decorates the __init__ to add a post_init hook, and the save method to trigger general tracking after saving and post_save signals have finished."""
        def init_decorator(previous_init):
            def new_init(self, *args, **kwargs):
                previous_init(self, *args, **kwargs)
                if type(self) == cls:
                    self.__post_init__()
            return new_init
        
        def save_decorator(previous_save):
            def new_save(self, *args, **kwargs):
                previous_save(self, *args, **kwargs)
                self._trigger_tracking_for_id(None)
            return new_save

        cls.__init__ = init_decorator(cls.__init__)
        cls.save = save_decorator(cls.save)

    def __post_init__(self):
        self._initial_state = self._get_current_values()
        self._state_store = {}