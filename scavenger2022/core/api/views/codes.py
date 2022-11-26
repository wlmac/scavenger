from rest_framework.decorators import api_view
from rest_framework.response import Response
from ...models import QrCode
__ALL__ = ['code', 'codes']

@api_view()
def code(request):
    """
    Returns the QR code data for the given code.
    example: ..qr/12
    """

    obj = QrCode.objects.get(id=request.GET.get('id'))

    return Response(obj)

@api_view()
def codes(request):
    return Response(QrCode.objects.all())
