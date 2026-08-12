# Self-Healing CI/CD Pipeline

A deployment pipeline that verifies its own work before committing to it. Every new commit is built, run alongside the currently-live version, and health-checked against a real dependency (the database) before it's ever given real traffic. If it fails, it's discarded automatically — production stays up, with no one needing to notice or intervene.

**Live dashboard:** [self-healing-pipeline.vercel.app] (https://self-healing-pipeline.vercel.app/)
*(reflects the last recorded deployment run — the AWS backend behind it was intentionally torn down after recording to avoid ongoing cost)*

**Demo video:** [\[link here\]](https://drive.google.com/file/d/1tDo1EyomKRoqNGHhjHMWTrPjQqgG-jX1/view?usp=sharing)

---

## The problem this solves

Most deployment setups push new code straight to production and hope it works. If it doesn't, the outage lasts until a human notices and manually rolls back — slow, and entirely dependent on someone watching. This pipeline removes that dependency: it verifies a deploy is actually healthy *before* it ever reaches real users, and rolls back automatically if it isn't.

## How it works

1. A push to `main` triggers Jenkins automatically via a GitHub webhook.
2. Jenkins builds a Docker image tagged with the commit's git SHA — never `latest`, so there's always something concrete to roll back to.
3. The new image is run as a **shadow container** — live traffic is still being served by the old version, untouched.
4. The shadow container's `/health/` endpoint is polled with retries. It checks two things: is the app running, and can it actually reach Postgres — not just "is the port open."
5. **If healthy:** the shadow container is renamed to the stable `live` name, Nginx is reloaded to point at it, and the old container is removed. Zero downtime.
6. **If unhealthy:** the shadow container is deleted. The live container was never touched — this *is* the rollback.
7. Either outcome is logged to a Postgres-backed Events API, which a Next.js dashboard reads to show live status and full deployment history.

```
git push
   │
   ▼
GitHub webhook → Jenkins
   │
   ▼
docker build (tagged by SHA)
   │
   ▼
Shadow deploy (no live traffic)
   │
   ▼
Health check (app + DB connectivity)
   │
   ├── healthy ──► Promote: reload Nginx, retire old container
   │
   └── unhealthy ──► Rollback: delete shadow, live container untouched
   │
   ▼
Log result → Events API → Postgres
   │
   ▼
Dashboard shows live status + history
```

## Tech stack

| Layer | Technology |
|---|---|
| Application | Django 5.2, PostgreSQL |
| API | Django REST Framework |
| Containerization | Docker |
| CI/CD | Jenkins |
| Reverse proxy | Nginx |
| Dashboard | Next.js 15 (App Router), TypeScript, Tailwind CSS, Framer Motion |
| Backend hosting | AWS EC2 (Ubuntu, free tier) |
| Frontend hosting | Vercel |

## Key design decisions

- **SHA-based image tags, never `latest`** — rollback only means something if there's a specific prior version to roll back to.
- **The old container is never touched until the new one proves itself.** Rollback isn't a special action the system takes — it's simply the absence of promotion.
- **Health checks verify real dependencies**, not process liveness. A container can be "up" and still be unable to reach its database — that's exactly the failure mode this pipeline is built to catch.
- **Distinct outcomes for promoted / rolled back / crashed.** A genuine pipeline crash is never silently reported as a normal rollback — conflating the two would hide real bugs.
- **Promotion is idempotent.** If a previous run crashed partway through, the next run cleans up that leftover state automatically rather than failing again.
- **Observability never blocks a real decision.** If the Events API is briefly unreachable, that's logged and ignored — it should never cause a false rollback or false promotion.

## Repository structure

```
backend/          Django app, health endpoint, Events API, deploy scripts, Dockerfile
  ├── core/
  ├── healthcheck/       # /health/ endpoint — app + DB connectivity checks
  ├── events/            # DRF API — deployment history
  ├── scripts/
  │   ├── deploy.py           # shadow deploy → health check → promote/rollback
  │   └── healthcheck_retry.py
  └── nginx/nginx.conf

frontend/          Next.js dashboard (live status + deployment timeline)

Jenkinsfile         Pipeline-as-code — Jenkins reads this file directly from
                    the repo via "Pipeline script from SCM", so the pipeline
                    logic is version-controlled like everything else, not
                    hidden in Jenkins' UI.
```

## Testing a rollback

Add `-e SIMULATE_FAILURE=true` to the shadow container's env vars in `deploy.py`'s `deploy_shadow()` function, push, and trigger a build — the health check will fail on the DB check by design, and the pipeline will roll back automatically while the previous version keeps serving traffic.

## Limitations / possible extensions

- Currently wired to this specific app — the pipeline *mechanism* is generic, but the repo URL, Dockerfile, env vars, and health-check path are hardcoded rather than parameterized. Turning these into CLI arguments would make it reusable across projects.
- The Events API's write endpoint is unauthenticated, which is fine for this demo scope but would need a shared secret before running long-term on a public server.
- `ALLOWED_HOSTS = ['*']` is a deliberate tradeoff for container-to-container health checks over a dynamic hostname — would be scoped down for a longer-lived deployment.

---

## 👤 Author

Built by **Yukti Singh**
📧 yuktisingh2005@gmail.com
