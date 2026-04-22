# 3. Context and Scope

## 3.1 Business Context

![System Context Diagram](diagrams/c4-context.svg)

| Neighbour | Communication | Direction |
|-----------|--------------|-----------|
| User (browser) | HTTPS — REST/JSON via React SPA | → Social Network |
| Email Provider | SMTP or HTTP API (e.g. SendGrid) | Social Network → |

## 3.2 Technical Context

| Channel | Protocol | Purpose |
|---------|----------|---------|
| Browser ↔ FastAPI | HTTPS / REST+JSON | All user-facing operations |
| FastAPI ↔ PostgreSQL | TCP — asyncpg driver | Persistent storage for all bounded contexts |
| FastAPI → Email Provider | HTTPS API | Account verification, notifications |

## 3.3 Bounded Context Map

The system is divided into three bounded contexts. They communicate exclusively through internal REST APIs — no shared database tables.

| Bounded Context | Responsibilities | Key Entities |
|----------------|-----------------|--------------|
| Users | Profiles, authentication, follow relationships | User, Profile, Follow |
| Posts / Timeline | Creating posts, reading personal and aggregated feeds | Post, Feed, Like |
| Messaging | Direct messages, mentions | Conversation, Message, Mention |

Cross-context calls:
- Posts/Timeline → Users: resolve author profile data
- Messaging → Users: resolve recipient profile data
- Messaging → Posts/Timeline: resolve mentioned post context
