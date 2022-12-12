from django.conf import settings
import datetime


def cutoff(request):
    return dict(
        CUTOFF=(cutoff := settings.CUTOFF),
        CUTOFF_BEFORE=cutoff > datetime.datetime.utcnow(),
        CUTOFF_UNTIL=cutoff - datetime.datetime.utcnow(),
        CUTON=(cuton := settings.CUTON),
        CUTON_BEFORE=cuton > datetime.datetime.utcnow(),
        CUTON_UNTIL=cuton - datetime.datetime.utcnow(),
    )
