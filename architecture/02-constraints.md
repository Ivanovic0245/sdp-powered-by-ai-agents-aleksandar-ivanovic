# 2. Constraints

## 2.1 Technical Constraints

| Constraint | Rationale |
|------------|-----------|
| Python 3.12 | Mandated runtime for all backend services |
| FastAPI | Chosen web framework; async-first, OpenAPI out of the box |
| PostgreSQL | Single relational database; one schema per bounded context |
| React | Mandated frontend technology |
| REST/JSON | Primary API style between frontend and backend |

## 2.2 Organisational Constraints

| Constraint | Rationale |
|------------|-----------|
| Bounded context ownership | Each bounded context (Users, Posts/Timeline, Messaging) is developed and deployed independently |
| OpenAPI-first | Every service must expose an OpenAPI 3.x spec before implementation begins |
| No shared database tables across bounded contexts | Cross-context data access goes through APIs only |

## 2.3 Conventions

| Convention | Detail |
|------------|--------|
| Code style | PEP 8, enforced via `ruff` |
| Branch strategy | GitHub Flow (feature branches + main) |
| Versioning | Semantic Versioning 2.0 for all services |
| Documentation | arc42 in Markdown, diagrams as PlantUML → SVG |
