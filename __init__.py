from . import ojad, lookup

try:
    from . import pronunciation, bulk_pronunciation
except ImportError:
    print("Failed to load pronunciation, probably not running in anki?")
