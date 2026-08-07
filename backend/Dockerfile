# Slim base image — smaller pull/build times, matters once Jenkins
# is rebuilding this on every push.
FROM python:3.12-slim

# Prevents Python from writing .pyc files and buffering stdout —
# the latter matters a lot for Docker logs to show up in real time.
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# Copy requirements first, install, THEN copy the rest of the code.
# This ordering matters for build caching: as long as requirements.txt
# doesn't change, Docker reuses the cached install layer even when
# your app code changes — much faster rebuilds during development.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# Gunicorn, not manage.py runserver — this is what actually runs
# in the container. "core.wsgi" refers to core/wsgi.py, matching
# your project name.
CMD ["gunicorn", "core.wsgi:application", "--bind", "0.0.0.0:8000"]