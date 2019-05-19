from . import ojad, lookup

try:
    from . import reading
except ImportError:
    print("Failed to load reading, probably not running in anki?")
