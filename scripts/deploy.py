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

NETWORK = "shp-network"
NGINX_CONF_PATH = "nginx/nginx.conf"
IMAGE_NAME = "self-healing-pipeline"

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


def deploy_shadow(sha: str, shadow_port: int) -> str:
    """Starts the new SHA-tagged image as a shadow container on its
    own port. Does NOT touch the live container."""
    shadow_name = f"shp-app-{sha}"

    if container_exists(shadow_name):
        run(["docker", "rm", "-f", shadow_name])

    run([
        "docker", "run", "--name", shadow_name,
        "--network", NETWORK,
        "-p", f"{shadow_port}:8000",
        *DB_ENV,
        "-e", f"GIT_SHA={sha}",
        "-d", f"{IMAGE_NAME}:{sha}",
    ])
    return shadow_name


def health_check(shadow_name: str) -> bool:
    """Uses the container's name over the Docker network, not
    localhost — Jenkins runs `docker run` against the host's Docker
    daemon via the mounted socket, making shadow containers SIBLINGS
    of Jenkins, not children. localhost inside Jenkins' own network
    namespace can't reach them; the shared Docker network can."""
    result = run([
        sys.executable, "scripts/healthcheck_retry.py",
        "--url", f"http://{shadow_name}:8000/health/",
        "--retries", "10", "--delay", "3",
    ], check=False)
    print(result.stdout)
    return result.returncode == 0


def promote(shadow_name: str, sha: str):
    """New container proved healthy. Rewrite Nginx's upstream to
    point at it, reload Nginx, then retire the old live container."""
    old_live_exists = container_exists("shp-app-live")

    # Rename shadow -> live BEFORE rewriting Nginx config, so the
    # hostname Nginx will proxy to already resolves on the network.
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

    print(f"PROMOTED: {sha} is now live")


def rollback(shadow_name: str, sha: str):
    """New container failed health checks. Kill it. The live
    container was never touched, so this is the entire rollback."""
    run(["docker", "rm", "-f", shadow_name])
    print(f"ROLLED BACK: {sha} failed health checks, previous version remains live")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--sha", required=True)
    parser.add_argument("--shadow-port", type=int, default=8092)
    args = parser.parse_args()

    shadow_name = deploy_shadow(args.sha, args.shadow_port)
    healthy = health_check(shadow_name)  
    if healthy:
        promote(shadow_name, args.sha)
        sys.exit(0)
    else:
        rollback(shadow_name, args.sha)
        sys.exit(1)


if __name__ == "__main__":
    main()