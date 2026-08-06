"""
Polls a /health/ endpoint with retries until it reports healthy,
or gives up after max attempts.

Usage:
    python healthcheck_retry.py --url http://localhost:8080/health/

Exit code 0 = healthy (success)
Exit code 1 = unhealthy after all retries exhausted (failure)

This script is what Jenkins Stage 3 calls after deploying the new
container. Its exit code is what decides promote vs. rollback.
"""

import argparse
import json
import sys
import time
import urllib.request
import urllib.error


def check_once(url: str) -> tuple[bool, dict]:
    """
    Makes a single request to the health endpoint.
    Returns (is_healthy, response_body_dict).
    Never raises — network errors are treated as "unhealthy",
    not as script crashes, because a connection refused (container
    not up yet) is an expected, retryable state, not a bug.
    """
    try:
        with urllib.request.urlopen(url, timeout=5) as response:
            body = json.loads(response.read().decode())
            return response.status == 200, body
    except urllib.error.HTTPError as e:
        # Server responded, but with an error status (e.g. 503).
        # We still want the body, since it has the failure reason.
        try:
            body = json.loads(e.read().decode())
        except Exception:
            body = {"error": f"HTTP {e.code}, unparseable body"}
        return False, body
    except Exception as e:
        # Connection refused, timeout, DNS failure, etc.
        # This happens legitimately right after a container starts.
        return False, {"error": str(e)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", required=True, help="Health endpoint URL to poll")
    parser.add_argument("--retries", type=int, default=10, help="Max attempts")
    parser.add_argument("--delay", type=int, default=3, help="Seconds between attempts")
    args = parser.parse_args()

    for attempt in range(1, args.retries + 1):
        healthy, body = check_once(args.url)
        print(f"[attempt {attempt}/{args.retries}] healthy={healthy} response={body}")

        if healthy:
            print("HEALTH CHECK PASSED")
            sys.exit(0)

        if attempt < args.retries:
            time.sleep(args.delay)

    print("HEALTH CHECK FAILED after all retries")
    sys.exit(1)


if __name__ == "__main__":
    main()