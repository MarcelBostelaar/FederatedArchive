from dataclasses import asdict, dataclass, field
from uuid import UUID

from archivebackend.models import Job

def serializeMapUUID(value):
    if type(value) == UUID:
        return {"uuid": str(value)}
    return value

@dataclass
class AbstractJobData:
    DatabaseJob : Job = field(init=False, default=None, metadata={"exclude": True})

    def serialize(self):
        values = asdict(self)
        if "JobType" not in values.keys():
            raise ValueError("JobType doesn't exist in job data.")
        return {
            k: serializeMapUUID(v) for k, v in values.items()
            if not self.__dataclass_fields__[k].metadata.get("exclude", False)
        }

    def __post_init__(self):
        for field_name, field_value in self.__dict__.items():
            if isinstance(field_value, dict) and "uuid" in field_value:
                self.__dict__[field_name] = UUID(field_value["uuid"])