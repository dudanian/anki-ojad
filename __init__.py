
try:
    from . import pronunciation, bulk_pronunciation, scraped_dict
except ImportError:
    print("Failed to load pronunciation, probably not running in anki?")
