import datetime

from core.models import Hunt
from django.utils import timezone


def start(request):
    now = timezone.now()
    if (hunt := Hunt.current_hunt()) is not None:
        event_start = hunt.start
        event_end = hunt.end
    elif Hunt.next_hunt() is not None:
        hunt = Hunt.next_hunt()
        event_start = hunt.start
        event_end = hunt.end
    else:
        print("WARNING: No hunt is scheduled")
        print("Please add a hunt in the future to the database")
        event_start = now + datetime.timedelta(weeks=75)
        event_end = event_start + datetime.timedelta(hours=3)

    return dict(
        START=event_start,
        START_BEFORE=event_start > now,
        START_UNTIL=event_start - now,
        END=event_end,
        END_BEFORE=event_end > now,
        END_UNTIL=event_end - now,
    )
