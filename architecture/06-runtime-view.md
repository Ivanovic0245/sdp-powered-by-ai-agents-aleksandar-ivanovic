# 6. Runtime View

## 6.1 User Registration and Login

```
Browser → Users Service: POST /auth/register {email, password}
Users Service → Users DB: INSERT user
Users Service → Email Provider: send verification email
Users Service → Browser: 201 Created

Browser → Users Service: POST /auth/login {email, password}
Users Service → Users DB: SELECT user, verify password hash
Users Service → Browser: 200 OK {access_token (JWT), refresh_token}
```

## 6.2 Post Creation

```
Browser → Posts Service: POST /posts {content}  [Bearer JWT]
Posts Service → Users Service: GET /users/{author_id}  (validate token, fetch profile)
Posts Service → Posts DB: INSERT post
Posts Service → Browser: 201 Created {post}
```

## 6.3 Timeline Feed (Fan-out on Read)

```
Browser → Posts Service: GET /feed  [Bearer JWT]
Posts Service → Users Service: GET /users/{user_id}/followees
Posts Service → Posts DB: SELECT posts WHERE author_id IN (followees) ORDER BY created_at DESC LIMIT 20
Posts Service → Users Service: GET /users/{id}  (batch — enrich each post with author profile)
Posts Service → Browser: 200 OK {posts[]}
```

## 6.4 Send Direct Message

```
Browser → Messaging Service: POST /conversations/{id}/messages {text}  [Bearer JWT]
Messaging Service → Users Service: GET /users/{recipient_id}  (verify recipient exists)
Messaging Service → Messaging DB: INSERT message
Messaging Service → Browser: 201 Created {message}
```

## 6.5 Mention Flow

```
Messaging Service: detects @username in message text
Messaging Service → Users Service: GET /users?username={handle}  (resolve mention target)
Messaging Service → Messaging DB: INSERT mention {message_id, target_user_id}
```

## 6.6 JWT Validation (all services)

Each service validates the JWT locally using the public RS256 key — no round-trip to the Users Service is required for token verification. The Users Service is only called when profile data is needed.
