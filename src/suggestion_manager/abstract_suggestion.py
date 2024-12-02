from functools import partial
from typing import Any
from typing_extensions import Annotated
from uuid import UUID
from pydantic import AfterValidator, BaseModel, Field, PlainSerializer, ValidationError

from suggestion_manager.models import SuggestedAction


def serializeSingleUUID(item):
    """Converts """
    return str(item.pk)

def serializeMultipleUUIDs(items):
    return [serializeSingleUUID(x) for x in items]

def validatorFunc(cls, x):
    if isinstance(x, str):
        try:
            x = UUID(x)
        except:
            raise ValidationError("Invalid UUID format: " + x)
        if cls.objects.filter(pk = x).count() == 1:
            return cls.objects.filter(pk = x).first()
        return None #no such item
    elif isinstance(x, cls):
        #Its already of correct type.
        return x
    else:
        raise ValidationError("Invalid type, should be string of format UUID or instance of " + cls.__name__)
    
def UUIDType(cls):
    return Annotated[
        Any, 
        PlainSerializer(serializeSingleUUID), 
        AfterValidator(partial(validatorFunc, cls)),
        "UUIDType"
    ]

def UUIDListType(cls):
    return Annotated[
        Any, 
        PlainSerializer(serializeMultipleUUIDs), 
        AfterValidator(lambda l: [x for x in (map(partial(validatorFunc, cls), l)) if x is not None]),
        "UUIDListType"
    ]

class AbstractSuggestion(BaseModel):
    DatabaseEntry : Any = Field(default=None, exclude=True)
    SuggestionType: str = Field(default=None)
    __child_suggestions_to_register__ = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.SuggestionType is None:
            raise ValueError("SuggestionType must be defined in subclass of Abstract")
        AbstractSuggestion.__child_suggestions_to_register__.append(cls)

    def save(self, title=None, description=""):
        """Saves the suggestion to the database."""
        if not self.should_be_added():
            return self
        
        if self.DatabaseEntry is None:
            if title is None:
                title = self.SuggestionType
            self.DatabaseEntry = SuggestedAction(title = title, description = "")

        self.DatabaseEntry.data = self.model_dump()
        self.DatabaseEntry.save()
        return self
    
    def post_execution(self):
        """Cleans suggestion, for example, splitting off the accepted parts into its own suggestion."""
        raise NotImplementedError("reevaluate_self must be implemented in subclass of AbstractSuggestion")
    
    def execute_suggestion(self):
        """Executes the suggestion."""
        raise NotImplementedError("execute_suggestion must be implemented in subclass of AbstractSuggestion")
    
    def should_be_added(self):
        """Returns whether the suggestion should be added to the database."""
        raise NotImplementedError("should_be_added must be implemented in subclass of AbstractSuggestion")
    