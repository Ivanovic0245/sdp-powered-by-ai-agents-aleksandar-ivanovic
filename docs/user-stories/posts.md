# Posts / Timeline Domain — Story Bundles

---

## POST-STORY-001 — Create a post ✅ [CORE]

AS A logged-in user
I WANT to publish a short-form post
SO THAT my followers can see it in their timeline feed

### SCENARIO 1: Successful post creation

**Scenario ID**: POST-STORY-001-S1

**GIVEN**
* The user is authenticated (valid JWT)
* The post text is non-empty and within the allowed length

**WHEN**
* The user submits the post form

**THEN**
* A post record is created in the `posts` schema with `author_id`, `text`, and `created_at`
* The API returns `201 Created` with the new post object

### SCENARIO 2: Empty post rejected

**Scenario ID**: POST-STORY-001-S2

**GIVEN**
* The user submits a post with an empty or whitespace-only text body

**WHEN**
* The request reaches the Posts Service

**THEN**
* The API returns `422 Unprocessable Entity` with error code `POST_TEXT_REQUIRED`
* No record is created

### SCENARIO 3: Post exceeds maximum length

**Scenario ID**: POST-STORY-001-S3

**GIVEN**
* The post text exceeds 280 characters

**WHEN**
* The request reaches the Posts Service

**THEN**
* The API returns `422 Unprocessable Entity` with error code `POST_TEXT_TOO_LONG`
* No record is created

### SCENARIO 4: Unauthenticated request rejected

**Scenario ID**: POST-STORY-001-S4

**GIVEN**
* The request carries no JWT or an expired JWT

**WHEN**
* `POST /posts` is called

**THEN**
* The API returns `401 Unauthorized`

**Architecture reference**: [Chapter 1 — Introduction and Goals](../../architecture/01-introduction-and-goals.md), [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md)

---

### POST-FE-001.1 — Compose post UI

AS A logged-in user
I WANT a text input area with a submit button to compose a post
SO THAT I can publish content from the timeline page

#### SCENARIO 1: Post submitted and appears in feed

**Scenario ID**: POST-FE-001.1-S1

**GIVEN**
* The user is on the timeline page and has typed text into the compose area

**WHEN**
* The user clicks "Post"

**THEN**
* A `POST /posts` request is sent with the Bearer JWT
* On `201 Created` the new post is prepended to the feed without a full page reload
* The compose area is cleared

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md)

---

### POST-FE-001.2 — Compose form validation

AS A logged-in user
I WANT the compose form to enforce length limits before submission
SO THAT I get immediate feedback without a round-trip to the server

#### SCENARIO 1: Character counter warns near limit

**Scenario ID**: POST-FE-001.2-S1

**GIVEN**
* The user is typing in the compose area

**WHEN**
* The text length reaches 260 characters

**THEN**
* A character counter shows remaining characters in amber

**WHEN**
* The text length exceeds 280 characters

**THEN**
* The counter turns red and the submit button is disabled

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md)

---

### POST-BE-001.1 — POST /posts endpoint

AS A Posts Service
I WANT to expose `POST /posts`
SO THAT authenticated users can create posts

#### SCENARIO 1: Valid post is persisted

**Scenario ID**: POST-BE-001.1-S1

**GIVEN**
* The request carries a valid RS256 JWT
* The body contains `{"text": "<non-empty string ≤280 chars>"}`

**WHEN**
* `POST /posts` is called

**THEN**
* A row is inserted into `posts.posts (id, author_id, text, created_at)`
* Response is `201 Created` with `{id, author_id, text, created_at}`

#### SCENARIO 2: JWT validated locally without calling Users Service

**Scenario ID**: POST-BE-001.1-S2

**GIVEN**
* The Posts Service has the RS256 public key in `JWT_PUBLIC_KEY`

**WHEN**
* Any authenticated request arrives

**THEN**
* The token is verified locally; no HTTP call to the Users Service is made for auth

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md), [Chapter 9 — Architecture Decisions](../../architecture/09-architecture-decisions.md)

---

### POST-BE-001.2 — Author profile enrichment

AS A Posts Service
I WANT to enrich post responses with the author's display name and avatar
SO THAT the frontend can render posts without a separate profile lookup

#### SCENARIO 1: Author profile fetched from Users Service

**Scenario ID**: POST-BE-001.2-S1

**GIVEN**
* A post has been created with `author_id`

**WHEN**
* The post is returned in any response

**THEN**
* The Posts Service calls `GET /users/{author_id}` on the Users Service
* The response includes `author: {id, username, display_name, avatar_url}`

#### SCENARIO 2: Users Service unavailable — graceful degradation

**Scenario ID**: POST-BE-001.2-S2

**GIVEN**
* The Users Service is unreachable

**WHEN**
* The Posts Service attempts to enrich the author profile

**THEN**
* The post is returned with `author: null`
* A structured warning is logged with the `trace_id`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 8 — Cross-Cutting Concepts](../../architecture/08-cross-cutting-concepts.md)

---

### POST-INFRA-001.1 — Posts Service containerised and deployable

AS AN operator
I WANT the Posts Service packaged as a Docker image
SO THAT it can be deployed independently behind the nginx reverse proxy

#### SCENARIO 1: Container starts and serves traffic

**Scenario ID**: POST-INFRA-001.1-S1

**GIVEN**
* A Docker image is built from the Posts Service source
* `DATABASE_URL` and `JWT_PUBLIC_KEY` are set as environment variables

**WHEN**
* The container starts

**THEN**
* The service is reachable on its configured port
* `GET /health` returns `200 OK`

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### POST-INFRA-001.2 — Posts schema migration

AS AN operator
I WANT an Alembic migration that creates the `posts.posts` table
SO THAT the Posts Service can persist user content

#### SCENARIO 1: Migration creates posts table with required index

**Scenario ID**: POST-INFRA-001.2-S1

**GIVEN**
* A PostgreSQL instance has no `posts` schema tables

**WHEN**
* `alembic upgrade head` is run for the Posts Service

**THEN**
* Table `posts.posts` exists with columns `(id, author_id, text, created_at)`
* The `(author_id, created_at DESC)` index is managed by the feed-story migration (POST-INFRA-002.2)

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md), [Chapter 9 — Architecture Decisions](../../architecture/09-architecture-decisions.md)

---

### POST-INFRA-001.3 — Event handling

*Not applicable — post creation is a synchronous operation at this stage. No async fan-out events are triggered (ADR-004 uses fan-out on read).*

---

### POST-INFRA-001.4 — Monitoring and alarms for Posts Service

AS AN operator
I WANT a health check endpoint and an error-rate alert on the Posts Service
SO THAT I am notified when post creation is degraded

#### SCENARIO 1: Health check returns 200

**Scenario ID**: POST-INFRA-001.4-S1

**GIVEN**
* The Posts Service is running and connected to its database

**WHEN**
* `GET /health` is called

**THEN**
* Response is `200 OK` with `{"status": "ok"}`

#### SCENARIO 2: Alert fires on elevated error rate

**Scenario ID**: POST-INFRA-001.4-S2

**GIVEN**
* Prometheus scrapes `/metrics` on the Posts Service every 15 seconds

**WHEN**
* The HTTP 5xx error rate exceeds 1% for 5 consecutive minutes

**THEN**
* An alert fires and is routed to the on-call channel

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../../architecture/08-cross-cutting-concepts.md)

---

## POST-STORY-002 — Read aggregated timeline feed ✅ [CORE]

AS A logged-in user
I WANT to see a paginated feed of posts from users I follow
SO THAT I can stay up to date with their content

### SCENARIO 1: Timeline returns posts from followees

**Scenario ID**: POST-STORY-002-S1

**GIVEN**
* The authenticated user follows at least one user who has posts

**WHEN**
* The user requests their timeline feed

**THEN**
* Posts from all followees are returned, sorted by `created_at DESC`
* Each post includes the author's `username` and `avatar_url`
* The response is paginated (default page size: 20)

### SCENARIO 2: Empty feed for user with no followees

**Scenario ID**: POST-STORY-002-S2

**GIVEN**
* The authenticated user follows nobody

**WHEN**
* The user requests their timeline feed

**THEN**
* The API returns `200 OK` with an empty `items` array and pagination metadata (`page`, `page_size`, `has_next`)

### SCENARIO 3: Pagination returns correct page

**Scenario ID**: POST-STORY-002-S3

**GIVEN**
* The user's followees have published more than 20 posts in total

**WHEN**
* The user requests page 2 (`?page=2&page_size=20`)

**THEN**
* The response contains posts 21–40 sorted by `created_at DESC`
* The response includes `page`, `page_size`, and `has_next` metadata

### SCENARIO 4: Feed loads within performance budget

**Scenario ID**: POST-STORY-002-S4

**GIVEN**
* The authenticated user follows up to 1 000 users

**WHEN**
* The timeline feed is requested

**THEN**
* The response is returned in under 500 ms (p95)

**Architecture reference**: [Chapter 1 — Introduction and Goals](../../architecture/01-introduction-and-goals.md), [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md), [Chapter 9 — Architecture Decisions](../../architecture/09-architecture-decisions.md)

---

### POST-FE-002.1 — Timeline feed page

AS A logged-in user
I WANT an infinite-scroll timeline page that loads posts from my followees
SO THAT I can browse content without manual pagination

#### SCENARIO 1: Initial feed loads on page open

**Scenario ID**: POST-FE-002.1-S1

**GIVEN**
* The authenticated user navigates to `/timeline`

**WHEN**
* The page mounts

**THEN**
* A `GET /feed` request is sent with the Bearer JWT
* Up to 20 posts are rendered, each showing author avatar, username, text, and timestamp

#### SCENARIO 2: Next page loads on scroll to bottom

**Scenario ID**: POST-FE-002.1-S2

**GIVEN**
* The user has scrolled to the bottom of the currently loaded posts
* `has_next` is `true` in the last response

**WHEN**
* The scroll threshold is crossed

**THEN**
* A `GET /feed?page=<next>` request is sent
* New posts are appended below existing ones without replacing them

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md)

---

### POST-BE-002.1 — GET /feed endpoint

AS A Posts Service
I WANT to expose `GET /feed`
SO THAT authenticated users can retrieve their aggregated timeline

#### SCENARIO 1: Feed query aggregates followee posts (fan-out on read)

**Scenario ID**: POST-BE-002.1-S1

**GIVEN**
* The request carries a valid JWT containing `user_id`
* The `users.follows` table has the caller's followee IDs (read via internal API call to Users Service)

**WHEN**
* `GET /feed?page=1&page_size=20` is called

**THEN**
* The Posts Service obtains the followee ID list from the Users Service via the follow-graph contract (candidate: `GET /users/{user_id}/followees`; cross-context interface to be formally defined in architecture docs)
* A single query selects from `posts.posts WHERE author_id = ANY(:followee_ids) ORDER BY created_at DESC LIMIT 20 OFFSET 0`
* Response is `200 OK` with `{items: [...], page, page_size, has_next}`

#### SCENARIO 2: Each post enriched with author profile

**Scenario ID**: POST-BE-002.1-S2

**GIVEN**
* The feed query returns N posts with distinct `author_id` values

**WHEN**
* The Posts Service builds the response

**THEN**
* Author profiles are fetched via a batch Users Service contract for the unique author IDs in the page (candidate: `GET /users?ids={id1},{id2},...`; cross-context interface to be formally defined in architecture docs)
* Each post item includes `author: {id, username, display_name, avatar_url}`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md), [Chapter 9 — Architecture Decisions](../../architecture/09-architecture-decisions.md)

---

### POST-BE-002.2 — Followees cross-context call (candidate contract)

AS A Posts Service
I WANT to retrieve a user's followee list from the Users Service
SO THAT the feed query knows which `author_id` values to include

**Note**: `GET /users/{user_id}/followees` is a candidate cross-context contract pending formal definition in architecture/05-building-block-view.md.

#### SCENARIO 1: Followee list returned successfully

**Scenario ID**: POST-BE-002.2-S1

**GIVEN**
* The Posts Service calls the Users-domain follow-graph contract (candidate: `GET /users/{user_id}/followees`) with the Bearer JWT

**WHEN**
* The Users Service processes the request

**THEN**
* A list of `followee_id` values is returned
* The Posts Service uses this list as the `author_id` filter in the feed query

#### SCENARIO 2: Users Service unavailable — empty feed returned

**Scenario ID**: POST-BE-002.2-S2

**GIVEN**
* The Users Service is unreachable

**WHEN**
* The Posts Service attempts to fetch followees

**THEN**
* The feed returns `200 OK` with an empty `items` array
* A structured warning is logged with the `trace_id`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 8 — Cross-Cutting Concepts](../../architecture/08-cross-cutting-concepts.md)

---

### POST-INFRA-002.1 — Posts Service containerised and deployable

*Covered by POST-INFRA-001.1 — the same container serves `/feed`.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### POST-INFRA-002.2 — Feed query index migration

AS AN operator
I WANT an Alembic migration that ensures the `(author_id, created_at DESC)` index exists on `posts.posts`
SO THAT fan-out-on-read feed queries meet the 500 ms performance budget

#### SCENARIO 1: Index present after migration

**Scenario ID**: POST-INFRA-002.2-S1

**GIVEN**
* The `posts.posts` table exists (POST-INFRA-001.2 has run)

**WHEN**
* The migration for POST-STORY-002 is applied

**THEN**
* `EXPLAIN ANALYZE` on the feed query shows an index scan on `(author_id, created_at DESC)`
* Migration is idempotent (`CREATE INDEX IF NOT EXISTS`)

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md), [Chapter 9 — Architecture Decisions](../../architecture/09-architecture-decisions.md)

---

### POST-INFRA-002.3 — Event handling

*Not applicable — the timeline feed is a synchronous read; no async events are triggered (ADR-004: fan-out on read).*

---

### POST-INFRA-002.4 — Feed latency alert

AS AN operator
I WANT an alert when feed response latency exceeds the 500 ms quality goal
SO THAT performance degradation is caught before users notice

#### SCENARIO 1: Latency alert fires on p95 breach

**Scenario ID**: POST-INFRA-002.4-S1

**GIVEN**
* Prometheus scrapes `/metrics` on the Posts Service and records `http_request_duration_seconds`

**WHEN**
* The p95 latency for `GET /feed` exceeds 500 ms for 5 consecutive minutes

**THEN**
* An alert fires and is routed to the on-call channel

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../../architecture/08-cross-cutting-concepts.md)

---

## POST-STORY-003 — Like / unlike a post ✅ [Supporting]

AS A logged-in user
I WANT to like or unlike a post
SO THAT I can express appreciation for content

### SCENARIO 1: Successfully like a post

**Scenario ID**: POST-STORY-003-S1

**GIVEN**
* The authenticated user has not already liked the post

**WHEN**
* The user clicks the like button on a post

**THEN**
* A like record is created in `posts.likes`
* The post's like count increments by 1
* The API returns `200 OK`

### SCENARIO 2: Unlike a post

**Scenario ID**: POST-STORY-003-S2

**GIVEN**
* The authenticated user has already liked the post

**WHEN**
* The user clicks the like button again

**THEN**
* The like record is removed from `posts.likes`
* The post's like count decrements by 1

### SCENARIO 3: Like is idempotent

**Scenario ID**: POST-STORY-003-S3

**GIVEN**
* The authenticated user has already liked the post

**WHEN**
* `POST /posts/{id}/like` is called again

**THEN**
* Response is `200 OK` with no duplicate like record created

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md)

---

### POST-FE-003.1 — Like button on post card

AS A logged-in user
I WANT a like toggle button on each post card
SO THAT I can like or unlike without leaving the feed

#### SCENARIO 1: Like count updates optimistically

**Scenario ID**: POST-FE-003.1-S1

**GIVEN**
* The user sees a post with a like button

**WHEN**
* The user clicks the like button

**THEN**
* The like count increments immediately (optimistic update)
* `POST /posts/{id}/like` is sent in the background
* On error the count reverts and a toast error is shown

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md)

---

### POST-BE-003.1 — POST /posts/{id}/like and DELETE /posts/{id}/like endpoints

AS A Posts Service
I WANT to expose `POST /posts/{id}/like` and `DELETE /posts/{id}/like`
SO THAT authenticated users can like and unlike posts

#### SCENARIO 1: Like created

**Scenario ID**: POST-BE-003.1-S1

**GIVEN**
* The request carries a valid JWT
* No existing like from this user on this post

**WHEN**
* `POST /posts/{id}/like` is called

**THEN**
* A row is inserted into `posts.likes (post_id, user_id, created_at)`
* Response is `200 OK` with updated `like_count`

#### SCENARIO 2: Unlike removes like

**Scenario ID**: POST-BE-003.1-S2

**GIVEN**
* A like record exists for this user and post

**WHEN**
* `DELETE /posts/{id}/like` is called

**THEN**
* The row is deleted from `posts.likes`
* Response is `200 OK` with updated `like_count`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md)

---

### POST-INFRA-003.1 — Posts Service containerised and deployable

*Covered by POST-INFRA-001.1.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### POST-INFRA-003.2 — likes table migration

AS AN operator
I WANT an Alembic migration that creates the `posts.likes` table
SO THAT like relationships can be persisted

#### SCENARIO 1: Migration creates likes table

**Scenario ID**: POST-INFRA-003.2-S1

**GIVEN**
* The `posts` schema exists (POST-INFRA-001.2 has run)

**WHEN**
* The migration for POST-STORY-003 is applied

**THEN**
* Table `posts.likes` exists with columns `(post_id, user_id, created_at)`
* A composite primary key on `(post_id, user_id)` prevents duplicate likes

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### POST-INFRA-003.3 — Event handling

*Not applicable — likes are synchronous; no async events required.*

---

### POST-INFRA-003.4 — Monitoring

*Covered by POST-INFRA-001.4.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

## POST-STORY-004 — Edit / delete own post ✅ [Supporting]

AS A logged-in user
I WANT to edit or delete a post I authored
SO THAT I can correct mistakes or remove content

### SCENARIO 1: Successfully edit a post

**Scenario ID**: POST-STORY-004-S1

**GIVEN**
* The authenticated user is the author of the post
* The new text is non-empty and ≤280 characters

**WHEN**
* The user submits the edited text

**THEN**
* The `posts.posts` row is updated with the new text and an `edited_at` timestamp
* The API returns `200 OK` with the updated post

### SCENARIO 2: Successfully delete a post

**Scenario ID**: POST-STORY-004-S2

**GIVEN**
* The authenticated user is the author of the post

**WHEN**
* The user confirms deletion

**THEN**
* The post row is deleted from `posts.posts`
* The API returns `204 No Content`

### SCENARIO 3: Non-author cannot edit or delete

**Scenario ID**: POST-STORY-004-S3

**GIVEN**
* The authenticated user is not the author of the post

**WHEN**
* `PATCH /posts/{id}` or `DELETE /posts/{id}` is called

**THEN**
* The API returns `403 Forbidden` with error code `NOT_POST_AUTHOR`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md)

---

### POST-FE-004.1 — Edit and delete controls on own post card

AS A logged-in user
I WANT edit and delete options on posts I authored
SO THAT I can manage my content inline

#### SCENARIO 1: Edit mode replaces post text with input

**Scenario ID**: POST-FE-004.1-S1

**GIVEN**
* The user is viewing their own post

**WHEN**
* The user clicks "Edit"

**THEN**
* The post text is replaced with an editable input pre-filled with the current text
* "Save" and "Cancel" buttons appear

#### SCENARIO 2: Delete requires confirmation

**Scenario ID**: POST-FE-004.1-S2

**GIVEN**
* The user clicks "Delete" on their own post

**WHEN**
* A confirmation dialog appears and the user confirms

**THEN**
* `DELETE /posts/{id}` is called and the post is removed from the feed on `204`

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md)

---

### POST-BE-004.1 — PATCH /posts/{id} and DELETE /posts/{id} endpoints

AS A Posts Service
I WANT to expose `PATCH /posts/{id}` and `DELETE /posts/{id}`
SO THAT authors can update or remove their posts

#### SCENARIO 1: Post updated by author

**Scenario ID**: POST-BE-004.1-S1

**GIVEN**
* The JWT `user_id` matches the post's `author_id`
* The body contains valid `{text}`

**WHEN**
* `PATCH /posts/{id}` is called

**THEN**
* `posts.posts` row is updated with new `text` and `edited_at = now()`
* Response is `200 OK` with the updated post

#### SCENARIO 2: Post deleted by author

**Scenario ID**: POST-BE-004.1-S2

**GIVEN**
* The JWT `user_id` matches the post's `author_id`

**WHEN**
* `DELETE /posts/{id}` is called

**THEN**
* The row is deleted from `posts.posts`
* Associated `posts.likes` rows are cascade-deleted
* Response is `204 No Content`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md)

---

### POST-INFRA-004.1 — Posts Service containerised and deployable

*Covered by POST-INFRA-001.1.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### POST-INFRA-004.2 — edited_at column migration

AS AN operator
I WANT an Alembic migration that adds `edited_at` to `posts.posts`
SO THAT edited posts can be distinguished from original ones

#### SCENARIO 1: Migration adds edited_at column

**Scenario ID**: POST-INFRA-004.2-S1

**GIVEN**
* The `posts.posts` table exists

**WHEN**
* The migration for POST-STORY-004 is applied

**THEN**
* Column `edited_at TIMESTAMPTZ NULL` exists on `posts.posts`
* Existing rows have `edited_at = NULL`

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### POST-INFRA-004.3 — Event handling

*Not applicable — edit and delete are synchronous operations.*

---

### POST-INFRA-004.4 — Monitoring

*Covered by POST-INFRA-001.4.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)
