from core.settings import settings
import IP2Location
from celery.task.control import inspect


# Check if celery is working
def is_celery_working():
    insp = inspect()
    status = insp.stats()
    return bool(status)

# Load location details based on IP
locationDatabaseIPv4 = IP2Location.IP2Location(settings.IPv4_LOCATION_FILE_PATH)
locationDatabaseIPv6 = IP2Location.IP2Location(settings.IPv6_LOCATION_FILE_PATH)
