import datetime

from core.models import Hunt
from django.conf import settings
from django.utils import timezone


def start(request):
    hunt = Hunt.current_hunt()
    now = timezone.now()
    return dict(
        START=(start := hunt.start),
        START_BEFORE=start > now,
        START_UNTIL=start - now,
        END=(end := hunt.end),
        END_BEFORE=end > now,
        END_UNTIL=end - now,
    )
