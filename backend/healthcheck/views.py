import os
from django.http import JsonResponse
from django.db import connection
from django.views.decorators.http import require_GET


@require_GET
def health(request):
    checks = {}

    # Check 1: the app process itself is running.
    # Trivially true if this code executed at all — but we still
    # report it explicitly so the JSON always shows all checks.
    checks["app"] = True

    # Check 2: real database connectivity.
    # We don't just check "is there a connection object" — we run
    # an actual query, because a stale/broken connection can exist
    # without being usable.
    try:
        # SIMULATE_FAILURE lets us force this branch on demand,
        # for testing the pipeline's rollback logic later without
        # needing to actually break the database.
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