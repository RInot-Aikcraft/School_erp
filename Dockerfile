FROM python:3.11-slim

# Dépendances système pour PostgreSQL
RUN apt-get update && apt-get install -y \
    libpq-dev gcc && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Installer Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt gunicorn

# Copier le projet
COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput

# Lancer Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "gestion_ecole.wsgi:application"]
