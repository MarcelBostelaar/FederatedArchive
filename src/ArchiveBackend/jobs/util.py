from dataclasses import fields, is_dataclass
from typing import Any, Dict

def tryConvertToDataclass(data: Dict[str, Any], cls: type):
    """Tries to convert a dictionary to a given dataclass."""
    if not is_dataclass(cls):
        raise ValueError(f"{cls} is not a dataclass.")

    for field in fields(cls):
        field_name = field.name
        field_type = field.type

        if field_name not in data:
            if field.default is not None or field.default_factory is not None:
                continue  # Field has a default, so it's optional
            else:
                return None  # Missing required field

        if not isinstance(data[field_name], field_type):
            try:
                field_type(data[field_name])  # Try casting
            except (ValueError, TypeError):
                return None  # Type mismatch

    return cls(**data)