"""Common utility functions for the Survey Assist project.

This module provides utility functions that can be reused across the project.
These functions are designed to handle common tasks such as type conversion
and error handling.
"""


def safe_int(value, default=0):
    """Safely convert a value to an integer, or return a default value.

    Args:
        value: The value to be converted to an integer. Can be of any type.
        default: The default value to return if conversion fails. Defaults to 0.

    Returns:
        int: The converted integer value, or the default value if conversion fails.
    """
    try:
        return int(value)
    except (ValueError, TypeError):
        return default
