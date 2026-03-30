"""Health check view — used by load balancers and k8s liveness/readiness probes."""
from django.db import connection, OperationalError

from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status


@api_view(['GET'])
@authentication_classes([])
@permission_classes([AllowAny])
def health_check(request):
    """
    GET /api/health/

    Returns 200 when the application is ready to serve traffic.
    Checks:
      - Application is running
      - Database is reachable

    Response:
      200 { "status": "ok", "database": "ok" }
      503 { "status": "degraded", "database": "unavailable" }
    """
    db_status = 'ok'
    http_status = status.HTTP_200_OK

    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
    except OperationalError:
        db_status = 'unavailable'
        http_status = status.HTTP_503_SERVICE_UNAVAILABLE

    return Response(
        {
            'status': 'ok' if http_status == 200 else 'degraded',
            'database': db_status,
        },
        status=http_status,
    )
