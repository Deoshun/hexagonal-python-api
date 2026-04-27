# Python Hexagonal Architecture w/ Github Workflows & Terraform Infrastucture

This is a python project that uses hexagonal architecture to expose buisness logic via both FastAPI and CLI tool


# Local Server Setup

```
docker build -t log-analyzer ./app
docker run -p 8000:8000 log-analyzer --env-file .env

```

# Cli Setup

```
pip install -e .

analyze --bucket my-logs --prefix logs/ --threshold 3
```


# How to Deploy

- Ensure AWS secrets are in GitHub.
- Push to main.
- GitHub Actions builds the ECR image and triggers Terraform.

# How to Test

```
pytest app/tests

```

# Design Decisions
- Memory: Streaming to save on mem.
- Security: Granular S3 IAM policies restricted to env-defined buckets.
- Networking: S3 Gateway Endpoint used to bypass NAT costs and latency.
