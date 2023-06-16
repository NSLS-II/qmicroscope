def convert_str_bool(val):
    """Converts a string representation of a boolean to a boolean value.

    Args:
        val (str): The string representation of the boolean.

    Returns:
        bool: The boolean value.
    """
    if isinstance(val, str):
        return True if val.lower() == "true" else False
    return val
