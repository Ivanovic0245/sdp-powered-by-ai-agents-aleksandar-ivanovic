# 11. Risks and Technical Debts

## 11.1 Risks

| ID | Risk | Probability | Impact | Mitigation |
|----|------|-------------|--------|------------|
| R-01 | PostgreSQL single instance becomes a bottleneck under high write load | Medium | High | Add read replicas for feed queries; evaluate partitioning on `posts` table by `created_at` |
| R-02 | Fan-out on read feed degrades as followee count grows beyond ~1 000 | Medium | High | Introduce a pre-computed feed cache (Redis) or switch to fan-out on write (see ADR-004) |
| R-03 | RS256 key rotation causes service downtime if not coordinated | Low | High | Implement a JWKS endpoint on the Users Service; services fetch keys dynamically |
| R-04 | Cross-context API calls create runtime coupling (cascading failures) | Medium | Medium | Add timeouts and circuit breakers (e.g. `httpx` with timeout + fallback) on all inter-service calls |
| R-05 | `common/` shared package becomes a coupling point across contexts | Medium | Medium | Keep `common/` limited to infrastructure concerns (JWT validation, error models); no domain logic |

## 11.2 Technical Debts

| ID | Debt | Impact | Remediation |
|----|------|--------|-------------|
| TD-01 | No caching layer — all feed queries hit PostgreSQL directly | Performance degrades at scale | Introduce Redis for feed and profile caching |
| TD-02 | No async task queue — email sending is synchronous in the request path | Increased latency on registration/notification endpoints | Offload to a task queue (e.g. Celery + Redis or ARQ) |
| TD-03 | No API versioning strategy defined | Breaking changes will affect all clients simultaneously | Adopt URL versioning (`/api/v1/`) from the first public release |
| TD-04 | Alembic migrations run on startup in development — risky if applied to production accidentally | Unintended schema changes in production | Enforce migration-only CI job; remove auto-migrate from startup in all environments |
