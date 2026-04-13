# Architecture Decisions

## ADR-001: Technology Stack Selection

**Status:** Accepted

**Context:**
We need to choose a language, framework, and data storage solution for the Social Network kata. The system needs to handle user posts, timelines, following relationships, mentions, and direct messages across three bounded contexts: Users, Posts/Timeline, and Messaging.

**Decision:**
- Language: Python 3.12
- Framework: FastAPI (REST API backend)
- Data Storage: PostgreSQL (relational, suits users, posts, and relationships)
- Frontend: React (single-page application)

**Rationale:**
- Python 3.12 is already the course standard and team-familiar
- FastAPI provides automatic OpenAPI docs and async support out of the box
- PostgreSQL handles relational data (users, posts, follows, messages) with strong consistency guarantees
- React is widely used and fits the course prerequisites

**Consequences:**
- Team must be familiar with Python async patterns
- PostgreSQL requires schema migrations on model changes
- Following relationships and timeline aggregation need careful query optimization at scale
