"""utils module."""
def try_float(s: str) -> bool:
    """Tries to convert a string to float.

    Args:
        s (str): String

    Returns:
        bool: True if able to transform, False otherwise
    """
    if not s:
        return False
    try:
        float(s.replace(',', '.'))
        return True
    except ValueError:
        return False