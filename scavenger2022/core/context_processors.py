from django.conf import settings
import datetime


def cutoff(request):
    return dict(
        CUTOFF=(cutoff := settings.CUTOFF),
        CUTOFF_BEFORE=cutoff > datetime.datetime.now(),
        CUTOFF_UNTIL=cutoff - datetime.datetime.now(),
    )
