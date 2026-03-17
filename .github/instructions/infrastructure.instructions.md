---
applyTo: "**/*.tf,**/Dockerfile,**/docker-compose*,**/.github/workflows/**,**/helm/**,**/k8s/**,**/Makefile"
---

# Infrastructure & DevOps Conventions

## Terraform

- Use reusable modules for each infrastructure component
- Use remote state (S3 + DynamoDB lock); never use local state in a team setup
- Use typed variables with `description` and `validation` blocks
- Document outputs for cross-module composition
- Run `terraform fmt` and `terraform validate` in pre-commit
- Naming: snake_case for resources, kebab-case for tags

## Docker

- Use multi-stage builds to reduce image size
- Use a minimal base image (Alpine or Distroless)
- Run as a non-root user (`USER node` or `USER appuser`)
- Maintain `.dockerignore`; never copy `node_modules`, `.git`, or `.env`
- Define health checks in the Dockerfile
- Do not use the `latest` tag; pin base image versions explicitly

## Kubernetes

- Use namespaces per environment and domain
- Set both resource requests and limits on every container
- Configure liveness, readiness, and startup probes
- Use PodDisruptionBudget for critical services
- Prefer HorizontalPodAutoscaler based on business metrics when possible
- Use external-secrets-operator for secrets; never commit plain-text secrets in manifests

## CI/CD (GitHub Actions)

- Enforce Conventional Commits in CI
- Pipeline: lint -> build -> test -> security scan -> deploy
- Separate environments: dev -> staging -> production
- Production deployment: blue-green or canary with automatic rollback
- Store secrets in GitHub Secrets; never in code
- Cache dependencies to speed up builds

## Observability

- Use OpenTelemetry for traces, metrics, and logs
- Use structured JSON logging with correlation IDs
- Expose health endpoints (`/health`, `/ready`) on every service
- Expose RED metrics (Rate, Error, Duration) in Prometheus format
