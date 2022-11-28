from django.http import JsonResponse
from ...models import QrCode, Hint

__ALL__ = ["code", "codes"]


def code(request, id):
    """
    Returns the QR code data for the given code.
    http://127.0.0.1:8001/api/qr/12

    """
    try:
        qr = QrCode.objects.get(id=id)
    except QrCode.DoesNotExist:
        return JsonResponse({"error": "QR code not found"}, status=404)
    qr_data = {'id': qr.id, 'location': qr.location}
    hints = list(Hint.objects.filter(qr_code=qr.id).values())
    for hint in hints:
        del hint['qr_code_id'], hint['id']

    return JsonResponse({'qr': qr_data, 'hints': hints})


def codes(request):
    All_codes = list(QrCode.objects.all().values())
    data = {"QRcodes": All_codes}
    return JsonResponse(data)



