# 10. Quality Requirements

## 10.1 Quality Tree

```
Quality
├── Performance
│   ├── Timeline feed response < 500 ms (p95)
│   └── Post creation response < 200 ms (p95)
├── Availability
│   └── Uptime ≥ 99.9% per calendar month
├── Scalability
│   └── Sustain 10 000 concurrent users without latency degradation
├── Security
│   ├── Unauthenticated access to protected endpoints returns 401
│   └── Users can only modify their own resources (403 otherwise)
├── Maintainability
│   └── A feature confined to one bounded context requires no changes in others
└── Usability
    └── API errors include actionable, human-readable messages
```

## 10.2 Quality Scenarios

| ID | Quality Attribute | Stimulus | Response | Measure |
|----|------------------|----------|----------|---------|
| QS-01 | Performance | User requests timeline feed (follows 500 users) | Feed returned | p95 latency < 500 ms |
| QS-02 | Performance | User creates a post | Post persisted and returned | p95 latency < 200 ms |
| QS-03 | Availability | Single service instance crashes | Load balancer routes to healthy replica | Recovery < 30 s, zero data loss |
| QS-04 | Scalability | 10 000 concurrent users active simultaneously | All requests served | p95 latency stays within QS-01/02 bounds |
| QS-05 | Security | Unauthenticated request to `GET /feed` | Request rejected | HTTP 401, no data leaked |
| QS-06 | Security | User A attempts to delete User B's post | Request rejected | HTTP 403, audit log entry written |
| QS-07 | Maintainability | New feature added to Messaging context | No changes required in Users or Posts services | Zero cross-context file changes in PR |
| QS-08 | Usability | Client sends invalid request body | Error response returned | HTTP 422 with per-field error detail |
