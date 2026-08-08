"""
Shadow-deploys a new SHA-tagged image, health-checks it, and either
promotes it to live or rolls back — leaving the currently-live
container completely untouched until the new one proves itself.

Usage:
    python scripts/deploy.py --sha <git-sha>
"""

import argparse
import subprocess
import sys
import time
import urllib.request
import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

NETWORK = "shp-network"
NGINX_CONF_PATH = os.path.join(SCRIPT_DIR, "..", "nginx", "nginx.conf")
IMAGE_NAME = "self-healing-pipeline"

EVENTS_API_URL = "http://shp-app-live:8000/api/events/"

DB_ENV = [
    "-e", "DB_NAME=pipelinedb",
    "-e", "DB_USER=postgres",
    "-e", "DB_PASSWORD=devpassword",
    "-e", "DB_HOST=pg-dev",
    "-e", "DB_PORT=5432",
]


def run(cmd: list[str], check=True) -> subprocess.CompletedProcess:
    """Runs a shell command, printing it first so the pipeline log
    always shows exactly what happened — important once this runs
    unattended inside Jenkins."""
    print(f"$ {' '.join(cmd)}")
    return subprocess.run(cmd, check=check, capture_output=True, text=True)


def container_exists(name: str) -> bool:
    result = run(["docker", "ps", "-a", "--filter", f"name=^{name}$", "--format", "{{.Names}}"], check=False)
    return name in result.stdout.strip().splitlines()


def deploy_shadow(sha: str) -> str:
    """No host port is published — the shadow container only needs
    to be reachable via the Docker network name (used by the health
    check and by Nginx after promotion), never via localhost. This
    avoids permanent port collisions once a shadow gets promoted and
    keeps whatever port it originally had."""
    shadow_name = f"shp-app-{sha}"

    if container_exists(shadow_name):
        run(["docker", "rm", "-f", shadow_name])

    run([
        "docker", "run", "--name", shadow_name,
        "--network", NETWORK,
        *DB_ENV,
        "-e", f"GIT_SHA={sha}",
        "-e", "SIMULATE_FAILURE=true",
        "-d", f"{IMAGE_NAME}:{sha}",
    ])
    return shadow_name


def health_check(shadow_name: str) -> tuple[bool, str | None]:
    """Returns (healthy, failure_reason). failure_reason is None when
    healthy — it's only meaningful on failure, extracted from the
    retry script's FINAL_REASON line so the dashboard can show the
    real cause instead of a generic message."""
    retry_script = os.path.join(SCRIPT_DIR, "healthcheck_retry.py")
    result = run([
        sys.executable, retry_script,
        "--url", f"http://{shadow_name}:8000/health/",
        "--retries", "10", "--delay", "3",
    ], check=False)
    print(result.stdout)

    if result.returncode == 0:
        return True, None

    reason = "Health check failed after retries"
    for line in result.stdout.splitlines():
        if line.startswith("FINAL_REASON: "):
            reason = line.replace("FINAL_REASON: ", "").strip()
            break

    return False, reason


def promote(shadow_name: str, sha: str):
    """New container proved healthy. Rewrite Nginx's upstream to
    point at it, reload Nginx, then retire the old live container."""

    # Defensive cleanup: if a previous run crashed after renaming to
    # "retiring" but before removing it, that name would still be
    # taken and break this rename. Always ensure it's free first.
    if container_exists("shp-app-retiring"):
        run(["docker", "rm", "-f", "shp-app-retiring"])

    old_live_exists = container_exists("shp-app-live")

    if old_live_exists:
        run(["docker", "rename", "shp-app-live", "shp-app-retiring"])

    run(["docker", "rename", shadow_name, "shp-app-live"])

    with open(NGINX_CONF_PATH, "w") as f:
        f.write(
            "events {}\n\nhttp {\n"
            "    upstream app {\n"
            "        server shp-app-live:8000;\n"
            "    }\n"
            "    server {\n"
            "        listen 80;\n"
            "        location / {\n"
            "            proxy_pass http://app;\n"
            "            proxy_set_header Host $host;\n"
            "            proxy_set_header X-Real-IP $remote_addr;\n"
            "        }\n"
            "    }\n}\n"
        )

    run(["docker", "exec", "shp-nginx", "nginx", "-s", "reload"])

    if old_live_exists:
        run(["docker", "rm", "-f", "shp-app-retiring"])

    report_event(sha, "promoted")
    print(f"PROMOTED: {sha} is now live")


def rollback(shadow_name: str, sha: str, reason: str):
    """New container failed health checks. Kill it. The live
    container was never touched, so this is the entire rollback."""
    run(["docker", "rm", "-f", shadow_name])
    report_event(sha, "rolled_back", reason=reason)
    print(f"ROLLED BACK: {sha} failed health checks, previous version remains live")


def report_event(git_sha: str, status: str, reason: str = None):
    """POSTs a deployment result to the Events API. Failures here
    are logged but never crash the pipeline — a broken events log
    should never block or falsely fail a real deploy decision."""
    payload = {"git_sha": git_sha, "status": status}
    if reason:
        payload["reason"] = reason

    try:
        data = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            EVENTS_API_URL, data=data,
            headers={"Content-Type": "application/json"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=5) as resp:
            print(f"Event reported: {resp.status}")
    except Exception as e:
        print(f"WARNING: failed to report event: {e}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", required=True)
    args = parser.parse_args()

    shadow_name = deploy_shadow(args.sha)
    healthy = health_check(shadow_name)

    shadow_name = deploy_shadow(args.sha)
    healthy, failure_reason = health_check(shadow_name)

    if healthy:
        try:
            promote(shadow_name, args.sha)
            sys.exit(0)
        except Exception as e:
            print(f"CRITICAL: promotion crashed partway through: {e}")
            print("Manual intervention may be required — check `docker ps` "
                  "and Nginx config state directly.")
            sys.exit(2)
    else:
        rollback(shadow_name, args.sha, failure_reason)
        sys.exit(1)


if __name__ == "__main__":
    main()