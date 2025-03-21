def format_bytes(size_in_bytes):
    """
    Format a byte size into appropriate units (bytes, KB, MB, GB, TB)
    with 1 decimal place for units larger than bytes.
    Uses US formatting conventions.

    Args:
        size_in_bytes (int): The size in bytes

    Returns:
        str: The formatted size string (e.g., "1,234 bytes", "1.2 KB", "2.5 MB")
    """
    if size_in_bytes < 1024:
        return f"{size_in_bytes:,} bytes"

    kb = size_in_bytes / 1024
    if kb < 1024:
        return f"{kb:.1f} KB"

    mb = kb / 1024
    if mb < 1024:
        return f"{mb:.1f} MB"

    gb = mb / 1024
    if gb < 1024:
        return f"{gb:.1f} GB"

    tb = gb / 1024
    return f"{tb:.1f} TB"

