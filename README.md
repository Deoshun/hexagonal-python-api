# Local

docker build -t log-analyzer ./app
docker run -p 8000:8000 log-analyzer

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
