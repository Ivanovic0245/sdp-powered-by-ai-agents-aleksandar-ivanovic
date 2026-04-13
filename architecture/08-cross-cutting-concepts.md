# 8. Cross-Cutting Concepts

## 8.1 Authentication & Authorisation

- JWT RS256 tokens issued by the Users Service on login
- All services validate tokens locally using the shared public key — no network call required
- Token payload carries `user_id`, `email`, and `roles`
- Tokens expire after 15 minutes; refresh tokens (opaque, stored in Users DB) are valid for 30 days

## 8.2 Error Handling

All services return errors in a uniform envelope:

```json
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "User with id 42 does not exist"
  }
}
```

FastAPI exception handlers map domain exceptions to HTTP status codes consistently across all services.

## 8.3 Logging

- Structured JSON logs (via `structlog`)
- Every request logged with `trace_id`, `user_id`, `method`, `path`, `status_code`, `duration_ms`
- `trace_id` is propagated via `X-Trace-Id` HTTP header across service calls

## 8.4 Observability

| Signal | Tooling |
|--------|---------|
| Logs | stdout → log aggregator (e.g. Loki) |
| Metrics | Prometheus `/metrics` endpoint on each service |
| Tracing | OpenTelemetry SDK; traces exported to Jaeger/Tempo |

## 8.5 Input Validation

- All request bodies validated by Pydantic v2 models
- Validation errors return `422 Unprocessable Entity` with field-level detail
- No raw SQL — all queries go through SQLAlchemy 2 to prevent injection

## 8.6 Database Migrations

- Managed by Alembic, one migration environment per bounded context
- Migrations run automatically on service startup in development; applied manually (CI gate) in production

## 8.7 CORS

- Configured on each FastAPI service to allow requests only from the known SPA origin
- Credentials (cookies / Authorization header) allowed explicitly

## 8.8 Rate Limiting

- Applied at the nginx layer: 100 requests/minute per IP for unauthenticated endpoints
- Authenticated endpoints: 1 000 requests/minute per `user_id` (via nginx `limit_req` or an API gateway)
