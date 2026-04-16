# User Stories — Social Network Kata

## Pareto Progress

**Core: 3/3 completed (100%) ✅ — 3 of 12 stories (25% ≈ Pareto 20%) deliver 80%+ of product value**

---

## API Route Convention

Endpoint examples in the user stories use service-level route shapes for readability (e.g. `POST /auth/login`, `GET /feed`). The public routes exposed externally via nginx are prefixed with `/api`:

- `POST /auth/login` in a story means public `POST /api/auth/login`
- `GET /feed` in a story means public `GET /api/feed`

This convention applies to all linked story files below.

---

## Story Inventory

### Users Domain

| ID | Story | Type | Status |
|----|-------|------|--------|
| USER-STORY-001 | Register an account | **CORE** | ✅ Done |
| USER-STORY-002 | Log in and receive a JWT | Supporting | ✅ Done |
| USER-STORY-003 | View and edit own profile | Supporting | ✅ Done |
| USER-STORY-004 | Follow / unfollow another user | Supporting | ✅ Done |
| USER-STORY-005 | List followers / followees | Supporting | ✅ Done |

### Posts / Timeline Domain

| ID | Story | Type | Status |
|----|-------|------|--------|
| POST-STORY-001 | Create a post | **CORE** | ✅ Done |
| POST-STORY-002 | Read aggregated timeline feed | **CORE** | ✅ Done |
| POST-STORY-003 | Like / unlike a post | Supporting | ✅ Done |
| POST-STORY-004 | Edit / delete own post | Supporting | ✅ Done |

### Messaging Domain

| ID | Story | Type | Status |
|----|-------|------|--------|
| MSG-STORY-001 | Send a direct message | Supporting | ✅ Done |
| MSG-STORY-002 | Read a conversation | Supporting | ✅ Done |
| MSG-STORY-003 | Mention a user in a message | Supporting | ✅ Done |

---

## Pareto Rationale

Total stories: 12 — Core: 3 (25% of stories, 80%+ of product value)

Core stories are the absolute minimum for the product to function:
- **USER-STORY-001** — without registration there are no users and no product
- **POST-STORY-001** — without post creation there is no content
- **POST-STORY-002** — the aggregated timeline feed is the primary value proposition of the platform

All other stories (login, profiles, follows, likes, messaging) add value but the product skeleton exists without them.

---

## Story Files

| File | Domain |
|------|--------|
| [users.md](users.md) | Users |
| [posts.md](posts.md) | Posts / Timeline |
| [messaging.md](messaging.md) | Messaging |
