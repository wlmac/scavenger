import datetime

from core.models import Hunt
from django.conf import settings


def start(request):
    hunt = Hunt.current_hunt()
    return dict(
        START=(start := hunt.start),
        START_BEFORE=start > datetime.datetime.utcnow(),
        START_UNTIL=start - datetime.datetime.utcnow(),
        END=(end := hunt.end),
        END_BEFORE=end > datetime.datetime.utcnow(),
        END_UNTIL=end - datetime.datetime.utcnow(),
    )
