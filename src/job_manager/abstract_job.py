import datetime
from functools import partial
from typing import Any
from typing_extensions import Annotated
from uuid import UUID
from pydantic import AfterValidator, BaseModel, Field, PlainSerializer, ValidationError, model_validator

from job_manager.jobs_registry import JobsRegistry
from job_manager.models import Job

def serializerFunc(item):
    """Converts """
    return str(item.pk)

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
        PlainSerializer(serializerFunc), 
        AfterValidator(partial(validatorFunc, cls)),
        "UUIDType"
    ]

def UUIDListType(cls):
    return Annotated[
        Any, 
        PlainSerializer(lambda l: map(serializerFunc, l)), 
        AfterValidator(lambda l: map(partial(validatorFunc, cls), l)),
        "UUIDListType"
    ]

class AbstractJob(BaseModel):
    DatabaseJob : Any = Field(default=None, exclude=True)
    JobType: str = Field(default=None)
    __child_jobs_to_register__ = []

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.JobType is None:
            raise ValueError("JobType must be defined in subclass of Abstract")
        AbstractJob.__child_jobs_to_register__.append(cls)

    def execute(self):
        """Executes the job."""
        raise NotImplementedError("Abstract function execute not implemented in job " + self.JobType)

    def save(self):
        """Saves the job to the database."""
        if self.DatabaseJob is None:
            return
        self.DatabaseJob.parameters = self.model_dump()
        self.DatabaseJob.save()


    #ensures that all UUID fields are loaded from the database.
    @model_validator(mode='after')
    def checkAllUUIDLoaded(self):
        allFields = self.__class__.model_fields
        for k, v in allFields.items():
            if "UUIDType" in v.metadata:
                if getattr(self, k) is None:
                    if self.DatabaseJob is not None:
                        #Job is already in database, so we can add error messages to it.
                        self.DatabaseJob.addMessage("Field " + k + " could not be found in the database.")
                        self.DatabaseJob.status = Job.JobStatus.failed
                        self.DatabaseJob.save()
                    else:
                        #Job is new, not yet in database, so its an error in the backend during creation, not an expired job. Code should halt and be fixed.
                        raise ValidationError("Field " + k + " could not be found in the database.")