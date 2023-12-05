import datetime

from django.contrib import messages
from django.utils import timezone

from core.models import Hunt


def hunt(request) -> dict:
    """
    returns:
        hunt: the current hunt or the closest hunt
        FUTURE_HUNT_EXISTS: bool, if a future hunt exists
    """

    return dict(
        hunt=Hunt.current_hunt() or Hunt.closest_hunt(),
        FUTURE_HUNT_EXISTS=Hunt.next_hunt() is not None,
    )


def start(request) -> dict:
    """
    returns info about the current/closest hunt
    return dict:
        START: start time of the current/closest hunt
        BEFORE_START: bool, if the current time is before the start time
        TIME_UNTIL_START: timedelta, time until the start time
        END: end time of the current/closest hunt
        BEFORE_END: bool, if the current time is before the end time
        TIME_UNTIL_END: timedelta, time until the end time
        IN_HUNT: bool, if the current time is between the start and end time
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
        BEFORE_START=event_start > now,
        TIME_UNTIL_START=event_start - now,
        END=event_end,
        BEFORE_END=event_end > now,
        TIME_UNTIL_END=event_end - now,
        IN_HUNT=(event_start < now < event_end),
    )
