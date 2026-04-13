# 7. Deployment View

## 7.1 Deployment Topology

```
Internet
   │
   ▼
[ Load Balancer / Reverse Proxy (nginx) ]
   │              │               │
   ▼              ▼               ▼
[Users Service] [Posts Service] [Messaging Service]
(FastAPI/uvicorn) (FastAPI/uvicorn) (FastAPI/uvicorn)
   │              │               │
   └──────────────┴───────────────┘
                  │
         [ PostgreSQL Server ]
          ┌───────┬──────────┐
          │users  │posts     │messaging
          │schema │schema    │schema
          └───────┴──────────┘

[ Static Hosting (CDN) ]
   └── React SPA (built assets)
```

## 7.2 Infrastructure Components

| Component | Technology | Notes |
|-----------|-----------|-------|
| Reverse proxy | nginx | TLS termination, path-based routing to services |
| API processes | uvicorn (1 worker per container) | Scaled horizontally via container replicas |
| Database | PostgreSQL 16 | Single instance; one schema per bounded context |
| Static hosting | CDN (e.g. S3 + CloudFront) | Serves pre-built React SPA |
| Container runtime | Docker / Docker Compose (dev), Kubernetes (prod) | |

## 7.3 Routing Rules (nginx)

| Path prefix | Upstream |
|-------------|----------|
| `/api/auth/*`, `/api/users/*` | Users Service |
| `/api/posts/*`, `/api/feed/*` | Posts Service |
| `/api/conversations/*`, `/api/messages/*` | Messaging Service |

## 7.4 Environment Configuration

Each service is configured via environment variables:

| Variable | Used by | Purpose |
|----------|---------|---------|
| `DATABASE_URL` | All services | asyncpg connection string |
| `JWT_PUBLIC_KEY` | Posts, Messaging | RS256 public key for token validation |
| `JWT_PRIVATE_KEY` | Users | RS256 private key for token issuance |
| `EMAIL_API_KEY` | Users | Email provider credentials |

## 7.5 Dev vs Production

| Concern | Development | Production |
|---------|------------|------------|
| Orchestration | Docker Compose | Kubernetes |
| Database | Single PostgreSQL container | Managed PostgreSQL (e.g. RDS) |
| TLS | Self-signed / none | Valid certificate via Let's Encrypt or ACM |
| Scaling | 1 replica per service | Horizontal pod autoscaling |
