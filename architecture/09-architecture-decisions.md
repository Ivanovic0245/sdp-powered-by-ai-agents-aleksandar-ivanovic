# 9. Architecture Decisions

## ADR-001: FastAPI as the Web Framework

**Status:** Accepted  
**Context:** The backend must expose REST APIs with automatic OpenAPI documentation and support high-concurrency I/O without blocking threads.  
**Decision:** Use FastAPI for all three bounded context services.  
**Rationale:** FastAPI is async-first, generates OpenAPI 3.x specs automatically via Pydantic models, and has strong community adoption in the Python ecosystem.  
**Consequences:** All route handlers must be `async def`; blocking calls (e.g. file I/O) must be offloaded with `run_in_executor`.

---

## ADR-002: One PostgreSQL Schema per Bounded Context

**Status:** Accepted  
**Context:** Three bounded contexts need persistent storage. Sharing tables would couple contexts at the database level.  
**Decision:** Use a single PostgreSQL instance with separate schemas: `users`, `posts`, `messaging`.  
**Rationale:** Schema-level isolation enforces context boundaries without the operational overhead of running three separate database servers. Cross-context queries are forbidden; data is fetched via API calls.  
**Consequences:** Each service connects with a role that has access only to its own schema. Cross-context joins are not possible by design.

---

## ADR-003: JWT RS256 for Authentication

**Status:** Accepted  
**Context:** Multiple services need to verify user identity without coupling to the Users Service on every request.  
**Decision:** Issue RS256-signed JWTs from the Users Service; all other services validate tokens locally using the public key.  
**Rationale:** Asymmetric signing allows any service to verify tokens without access to the private key or a network call, keeping services loosely coupled.  
**Consequences:** The RS256 public key must be distributed to all services (via environment variable). Key rotation requires a coordinated redeployment.

---

## ADR-004: Fan-out on Read for Timeline Feed

**Status:** Accepted  
**Context:** A user's timeline aggregates posts from all followees. Two strategies exist: fan-out on write (pre-compute per follower) and fan-out on read (query at request time).  
**Decision:** Use fan-out on read: query the posts of all followees at request time, paginated and sorted by `created_at`.  
**Rationale:** At the current scale (≤10 000 concurrent users) fan-out on read is simpler to implement and avoids write amplification for users with many followers. Can be revisited if read latency becomes a bottleneck.  
**Consequences:** Feed query performance depends on the number of followees. An index on `(author_id, created_at DESC)` in the posts table is required.

---

## ADR-005: Modular Monorepo over Microservices

**Status:** Accepted  
**Context:** Three bounded contexts could be deployed as fully independent microservices or co-located in a monorepo.  
**Decision:** Single Git repository; three independently deployable FastAPI processes.  
**Rationale:** Monorepo simplifies cross-context refactoring, shared tooling (linting, CI), and onboarding while still allowing independent scaling and deployment of each service.  
**Consequences:** Shared libraries (e.g. JWT validation, error models) live in a `common/` package within the repo. Changes to `common/` affect all services and require coordinated releases.
