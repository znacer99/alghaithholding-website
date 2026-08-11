FROM python:3.10-slim-bullseye

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential gcc python3-dev libssl-dev libffi-dev libncurses-dev libreadline-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel
RUN pip install --no-cache-dir --force-reinstall -r requirements.txt

COPY . .

RUN touch db.sqlite

EXPOSE 5000
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app", "--workers", "3"]
