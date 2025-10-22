# Deployment Guide

This document describes several options for deploying Sentiment Spotlight.

## Prerequisites

- Docker 24+
- Access to a container registry (e.g., GitHub Container Registry, Docker Hub)
- Optional: Infrastructure to run containers (Render, Fly.io, Kubernetes, etc.)

## Building the image

```bash
docker build -t sentiment-spotlight:latest .
```

## Running locally with Docker

```bash
docker run --rm -p 8000:8000 sentiment-spotlight:latest
```

Open <http://127.0.0.1:8000> to access the UI or call the JSON API.

## Publishing to a registry

Replace `REGISTRY` and `YOUR_USERNAME` with your own identifiers.

```bash
docker tag sentiment-spotlight:latest REGISTRY/YOUR_USERNAME/sentiment-spotlight:latest
docker push REGISTRY/YOUR_USERNAME/sentiment-spotlight:latest
```

## Kubernetes deployment example

Below is a minimal Kubernetes manifest. Update the container image reference before
applying.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: sentiment-spotlight
spec:
  replicas: 2
  selector:
    matchLabels:
      app: sentiment-spotlight
  template:
    metadata:
      labels:
        app: sentiment-spotlight
    spec:
      containers:
        - name: app
          image: REGISTRY/YOUR_USERNAME/sentiment-spotlight:latest
          ports:
            - containerPort: 8000
          readinessProbe:
            httpGet:
              path: /health
              port: 8000
            initialDelaySeconds: 5
            periodSeconds: 10
---
apiVersion: v1
kind: Service
metadata:
  name: sentiment-spotlight
spec:
  selector:
    app: sentiment-spotlight
  ports:
    - protocol: TCP
      port: 80
      targetPort: 8000
  type: LoadBalancer
```

## GitHub Actions deployment hooks

The repository ships with a CI workflow (`.github/workflows/ci.yml`) that installs
dependencies and executes the tests. Extend that workflow with deployment steps (for
example, publishing the Docker image) once you have configured credentials.
