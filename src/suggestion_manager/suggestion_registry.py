from __future__ import annotations

suggestionTypes = {}

def SuggestionRegistry(cls):
    """Registers a suggestion class for conversion from json."""
    suggestionname = cls.model_fields["SuggestionType"].default
    if not isinstance(suggestionname, str):
        raise ValueError("SuggestionType must be a string.")
    if suggestionname in suggestionTypes:
        raise ValueError(f"Suggestion {suggestionname} already registered.")
    suggestionTypes[suggestionname] = cls

def suggestionConverter(data):
    """Converts a dictionary to a Suggestion object."""
    name = data["SuggestionType"]
    if name not in suggestionTypes:
        raise ValueError(f"Suggestion {name} not registered.")
    return suggestionTypes[name].parse_object(data)