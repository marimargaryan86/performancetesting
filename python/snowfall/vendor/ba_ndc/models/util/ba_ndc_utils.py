"""Contains utilities."""
import re


def snake_to_camel(string: str) -> str:
    """Convert a string in snake case to camel case."""
    return re.sub("_(.)", lambda word: word.group(1).upper(), string)
