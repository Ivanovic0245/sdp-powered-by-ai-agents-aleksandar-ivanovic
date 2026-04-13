# 12. Glossary

| Term | Definition |
|------|------------|
| **Bounded Context** | A explicit boundary within which a domain model applies. The system has three: Users, Posts/Timeline, Messaging. |
| **JWT (JSON Web Token)** | A compact, self-contained token used to transmit authentication claims between parties. Signed with RS256 in this system. |
| **RS256** | RSA Signature with SHA-256. An asymmetric signing algorithm where the private key signs and the public key verifies. |
| **Fan-out on Read** | A feed strategy where the timeline is assembled at query time by fetching posts from all followees. |
| **Fan-out on Write** | A feed strategy where a post is pushed into each follower's feed at write time. Not currently used (see ADR-004). |
| **FastAPI** | An async Python web framework that generates OpenAPI documentation automatically from Pydantic models. |
| **asyncpg** | A high-performance async PostgreSQL driver for Python, used via SQLAlchemy 2's async engine. |
| **Alembic** | A database migration tool for SQLAlchemy. Each bounded context has its own Alembic environment. |
| **Pydantic** | A Python data validation library used by FastAPI for request/response schema definition and validation. |
| **OpenAPI** | A specification standard for describing REST APIs. FastAPI generates an OpenAPI 3.x document automatically. |
| **Trace ID** | A unique identifier attached to a request and propagated across service calls via `X-Trace-Id` header for distributed tracing. |
| **Schema (PostgreSQL)** | A namespace within a PostgreSQL database. Used here to isolate each bounded context (`users`, `posts`, `messaging`). |
| **SPA (Single-Page Application)** | A web application that loads once and updates dynamically. The frontend is built with React. |
| **ADR (Architecture Decision Record)** | A document capturing a significant architectural decision, its context, rationale, and consequences. |
| **JWKS (JSON Web Key Set)** | A JSON document exposing public keys used to verify JWTs. Referenced as a future improvement for key rotation (R-03). |
| **Circuit Breaker** | A resilience pattern that stops calling a failing service after a threshold of errors, preventing cascading failures. |
| **Mention** | A reference to another user within a post or message, denoted by `@username`. |
| **Follow** | A directed relationship where one user subscribes to another user's posts. |
| **Timeline / Feed** | An aggregated, chronologically sorted list of posts from users that the current user follows. |
