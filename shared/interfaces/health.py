from django.http import JsonResponse


def health_check(request):
    """Endpoint publico y sin autenticacion para que Render (o cualquier
    balanceador) sepa si el contenedor esta listo para recibir trafico."""
    return JsonResponse({"status": "ok"})
