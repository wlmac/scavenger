import datetime
from typing import Dict

from django.contrib import messages
from django.utils import timezone

from core.models import Hunt

def hunt(request) -> Dict[str, Hunt]:
    """
    returns the current hunt
    """
    return dict(hunt=Hunt.current_hunt() or Hunt.closest_hunt())

def start(request) -> dict:
    """
    returns info about the current/closest hunt
    return dict:
        START: start time of the current/closest hunt
        START_BEFORE: bool, if the current time is before the start time
        START_UNTIL: timedelta, time until the start time
        END: end time of the current/closest hunt
        END_BEFORE: bool, if the current time is before the end time
        END_UNTIL: timedelta, time until the end time
    """
    now = timezone.now()
    if Hunt.objects.count() == 0:
        messages.add_message(
            request,
            messages.WARNING,
            "No hunts are in the database. Please contact an admin to add a hunt to the database",
        )
        event_start = now + datetime.timedelta(weeks=75)
        event_end = event_start + datetime.timedelta(hours=3)
    elif (hunt := Hunt.current_hunt()) is not None:
        event_start = hunt.start
        event_end = hunt.end
    elif Hunt.next_hunt() is not None:
        hunt = Hunt.next_hunt()
        event_start = hunt.start
        event_end = hunt.end
    else:
        closest_hunt = Hunt.closest_hunt()
        event_start = closest_hunt.start
        event_end = closest_hunt.end

    return dict(
        START=event_start,
        START_BEFORE=event_start > now,
        START_UNTIL=event_start - now,
        END=event_end,
        END_BEFORE=event_end > now,
        END_UNTIL=event_end - now,
    )
