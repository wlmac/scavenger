from django.conf import settings
import datetime


def start(request):
    return dict(
        START=(start := settings.START),
        START_BEFORE=start > datetime.datetime.utcnow(),
        START_UNTIL=start - datetime.datetime.utcnow(),
        END=(end := settings.END),
        END_BEFORE=end > datetime.datetime.utcnow(),
        END_UNTIL=end - datetime.datetime.utcnow(),
    )
