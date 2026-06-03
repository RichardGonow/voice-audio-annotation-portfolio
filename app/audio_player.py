SUPPORTED_FORMATS = {".wav", ".mp3"}


def is_supported(filename: str) -> bool:
    from pathlib import Path
    return Path(filename).suffix.lower() in SUPPORTED_FORMATS
