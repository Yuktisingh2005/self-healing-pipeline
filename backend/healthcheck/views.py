import os
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    checks = {}

    
    checks["app"] = True

    try:
       
        if os.environ.get("SIMULATE_FAILURE") == "true":
            raise Exception("Simulated DB failure (SIMULATE_FAILURE=true)")

        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        checks["db"] = True
    except Exception as e:
        checks["db"] = False
        checks["db_error"] = str(e)

    healthy = all(v for k, v in checks.items() if k in ("app", "db"))
    status_code = 200 if healthy else 503

    return JsonResponse(
        {
            "status": "healthy" if healthy else "unhealthy",
            "checks": checks,
            "git_sha": os.environ.get("GIT_SHA", "unknown"),
        },
        status=status_code,
    )