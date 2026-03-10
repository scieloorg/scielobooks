FROM python:3.12-slim
ENV PYTHONUNBUFFERED=1

ARG BUILD_DATE
ARG VCS_REF
ARG WEBAPP_VERSION

ENV IMAGE_BUILD_DATE=${BUILD_DATE}
ENV IMAGE_VCS_REF=${VCS_REF}
ENV IMAGE_WEBAPP_VERSION=${WEBAPP_VERSION}

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      build-essential \
      libpq-dev \
      libjpeg-dev \
      zlib1g-dev \
      libfreetype6-dev \
      libgif-dev \
      ca-certificates && \
    rm -rf /var/lib/apt/lists/*

COPY . /app
COPY production-TEMPLATE.ini /app/production.ini
WORKDIR /app

RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r /app/requirements.txt && \
    python setup.py install

EXPOSE 8000
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--paste", "/app/production.ini"]
