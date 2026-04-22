# Users Domain — Story Bundles

## USER-STORY-001 — Register an account ✅ [CORE]

AS A visitor
I WANT to create an account with my email and password
SO THAT I can access the social network as an authenticated user

### SCENARIO 1: Successful registration

**Scenario ID**: USER-STORY-001-S1

**GIVEN**
* The visitor is on the registration page
* The email address is not already registered

**WHEN**
* The visitor submits a valid email, username, and password

**THEN**
* A new user record is created in the `users` schema
* A verification email is dispatched via the Email Provider
* The visitor receives a `201 Created` response with the new user's public profile

### SCENARIO 2: Duplicate email rejected

**Scenario ID**: USER-STORY-001-S2

**GIVEN**
* An account with the submitted email already exists

**WHEN**
* The visitor submits the registration form

**THEN**
* The API returns `409 Conflict` with error code `EMAIL_ALREADY_EXISTS`
* No new record is created

### SCENARIO 3: Invalid input rejected

**Scenario ID**: USER-STORY-001-S3

**GIVEN**
* The visitor submits a registration form with a missing or malformed field (e.g. invalid email format, password too short)

**WHEN**
* The request reaches the Users Service

**THEN**
* The API returns `422 Unprocessable Entity` with field-level validation detail
* No new record is created

**Architecture reference**: [Chapter 1 — Introduction and Goals](../architecture/01-introduction-and-goals.md), [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-FE-001.1 — Registration page

AS A visitor
I WANT a registration form with fields for email, username, and password
SO THAT I can submit my details to create an account

#### SCENARIO 1: Form renders correctly

**Scenario ID**: USER-FE-001.1-S1

**GIVEN**
* The visitor navigates to `/register`

**WHEN**
* The page loads

**THEN**
* Fields for email, username, and password are visible and focusable
* A submit button is present and labelled "Create account"

**Architecture reference**: [Chapter 3 — Context and Scope](../architecture/03-context-and-scope.md)

---

### USER-FE-001.2 — Registration form validation

AS A visitor
I WANT inline validation feedback on the registration form
SO THAT I can correct errors before submitting

#### SCENARIO 1: Invalid email format shown inline

**Scenario ID**: USER-FE-001.2-S1

**GIVEN**
* The visitor has typed an invalid email (e.g. `notanemail`)

**WHEN**
* The visitor moves focus away from the email field

**THEN**
* An inline error message "Enter a valid email address" appears beneath the field
* The form cannot be submitted

#### SCENARIO 2: Duplicate email error surfaced from API

**Scenario ID**: USER-FE-001.2-S2

**GIVEN**
* The visitor submits a valid form
* The API returns `409 Conflict`

**WHEN**
* The response is received

**THEN**
* A banner error "This email is already registered" is displayed
* The form remains editable

**Architecture reference**: [Chapter 3 — Context and Scope](../architecture/03-context-and-scope.md)

---

### USER-BE-001.1 — POST /auth/register endpoint

AS A Users Service
I WANT to expose `POST /auth/register`
SO THAT visitors can create accounts

#### SCENARIO 1: Valid payload creates user

**Scenario ID**: USER-BE-001.1-S1

**GIVEN**
* The request body contains a unique email, a valid username, and a password of ≥8 characters

**WHEN**
* `POST /auth/register` is called

**THEN**
* A `users` row is inserted with a bcrypt-hashed password
* Response is `201 Created` with `{id, username, email, created_at}`

#### SCENARIO 2: Duplicate email returns 409

**Scenario ID**: USER-BE-001.1-S2

**GIVEN**
* A user with the same email already exists in the `users` schema

**WHEN**
* `POST /auth/register` is called with that email

**THEN**
* Response is `409 Conflict` with `{"error": {"code": "EMAIL_ALREADY_EXISTS", "message": "..."}}`
* No row is inserted

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../architecture/06-runtime-view.md)

---

### USER-BE-001.2 — Email verification dispatch

AS A Users Service
I WANT to send a verification email after successful registration
SO THAT only valid email addresses are activated

#### SCENARIO 1: Verification email sent on registration

**Scenario ID**: USER-BE-001.2-S1

**GIVEN**
* A new user record has just been created

**WHEN**
* The registration handler completes successfully

**THEN**
* A call is made to the Email Provider API with the verification link
* The `users` row has `email_verified = false` until the link is clicked

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

### USER-INFRA-001.1 — Users Service containerised and deployable

AS AN operator
I WANT the Users Service packaged as a Docker image
SO THAT it can be deployed independently behind the nginx reverse proxy

#### SCENARIO 1: Container starts and serves traffic

**Scenario ID**: USER-INFRA-001.1-S1

**GIVEN**
* A Docker image is built from the Users Service source
* `DATABASE_URL`, `JWT_PRIVATE_KEY`, and `EMAIL_API_KEY` are set as environment variables

**WHEN**
* The container starts

**THEN**
* The service is reachable on its configured port
* `GET /health` returns `200 OK`

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)

---

### USER-INFRA-001.2 — Users schema migration

AS AN operator
I WANT an Alembic migration that creates the `users` schema tables
SO THAT the Users Service has the persistent storage it needs

#### SCENARIO 1: Migration runs successfully on a clean database

**Scenario ID**: USER-INFRA-001.2-S1

**GIVEN**
* A PostgreSQL instance has no `users` schema tables

**WHEN**
* `alembic upgrade head` is run for the Users Service

**THEN**
* Tables `users` and `email_verifications` exist in the `users` schema
* The migration is idempotent (running it twice does not error)

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

### USER-INFRA-001.3 — Verification email event handler

AS AN operator
I WANT the email dispatch to be handled reliably after registration
SO THAT transient Email Provider failures do not fail the registration response

#### SCENARIO 1: Email sent after successful user insert

**Scenario ID**: USER-INFRA-001.3-S1

**GIVEN**
* The user row has been committed to the database

**WHEN**
* The post-registration hook fires

**THEN**
* The Email Provider API is called with the correct verification URL
* A failure to reach the Email Provider is logged but does not roll back the user record

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

### USER-INFRA-001.4 — Monitoring and alarms for Users Service

AS AN operator
I WANT a health check endpoint and an error-rate alert on the Users Service
SO THAT I am notified when registration or login is degraded

#### SCENARIO 1: Health check returns 200

**Scenario ID**: USER-INFRA-001.4-S1

**GIVEN**
* The Users Service is running and connected to its database

**WHEN**
* `GET /health` is called

**THEN**
* Response is `200 OK` with `{"status": "ok"}`

#### SCENARIO 2: Alert fires on elevated error rate

**Scenario ID**: USER-INFRA-001.4-S2

**GIVEN**
* The Prometheus `/metrics` endpoint is scraped every 15 seconds

**WHEN**
* The HTTP 5xx error rate on the Users Service exceeds 1% for 5 consecutive minutes

**THEN**
* An alert fires and is routed to the on-call channel

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

## USER-STORY-002 — Log in and receive a JWT ✅ [Supporting]

AS A registered user
I WANT to log in with my email and password
SO THAT I receive a JWT that grants me access to protected features

### SCENARIO 1: Successful login

**Scenario ID**: USER-STORY-002-S1

**GIVEN**
* The user has a verified account

**WHEN**
* The user submits correct email and password

**THEN**
* The API returns `200 OK` with a short-lived RS256 JWT (`access_token`) and an opaque `refresh_token`
* The JWT payload contains `user_id`, `email`, and `roles`

### SCENARIO 2: Wrong password rejected

**Scenario ID**: USER-STORY-002-S2

**GIVEN**
* The user submits a correct email but an incorrect password

**WHEN**
* `POST /auth/login` is called

**THEN**
* The API returns `401 Unauthorized` with error code `INVALID_CREDENTIALS`
* No token is issued

### SCENARIO 3: Unknown email rejected

**Scenario ID**: USER-STORY-002-S3

**GIVEN**
* The submitted email does not match any user record

**WHEN**
* `POST /auth/login` is called

**THEN**
* The API returns `401 Unauthorized` with error code `INVALID_CREDENTIALS`
* The response is indistinguishable from the wrong-password case (no user enumeration)

**Architecture reference**: [Chapter 1 — Introduction and Goals](../architecture/01-introduction-and-goals.md), [Chapter 5 — Building Block View](../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../architecture/06-runtime-view.md)

---

### USER-FE-002.1 — Login page

AS A registered user
I WANT a login form with email and password fields
SO THAT I can authenticate and be redirected to my timeline

#### SCENARIO 1: Successful login redirects to timeline

**Scenario ID**: USER-FE-002.1-S1

**GIVEN**
* The user is on `/login`

**WHEN**
* The user submits valid credentials and the API returns `200 OK`

**THEN**
* The `access_token` is stored in memory (not localStorage)
* The `refresh_token` is stored as an `HttpOnly` cookie
* The user is redirected to `/timeline`

**Architecture reference**: [Chapter 3 — Context and Scope](../architecture/03-context-and-scope.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

### USER-FE-002.2 — Login error handling

AS A registered user
I WANT clear feedback when my credentials are wrong
SO THAT I know to correct them without exposing security details

#### SCENARIO 1: Invalid credentials show generic error

**Scenario ID**: USER-FE-002.2-S1

**GIVEN**
* The user submits the login form
* The API returns `401 Unauthorized`

**WHEN**
* The response is received

**THEN**
* A banner error "Invalid email or password" is displayed
* The password field is cleared
* No token is stored

**Architecture reference**: [Chapter 3 — Context and Scope](../architecture/03-context-and-scope.md)

---

### USER-BE-002.1 — POST /auth/login endpoint

AS A Users Service
I WANT to expose `POST /auth/login`
SO THAT registered users can obtain a JWT

#### SCENARIO 1: Valid credentials return tokens

**Scenario ID**: USER-BE-002.1-S1

**GIVEN**
* The request body contains a registered email and the correct password

**WHEN**
* `POST /auth/login` is called

**THEN**
* The bcrypt hash is verified
* Response is `200 OK` with `{access_token, token_type: "bearer", expires_in: 900}`
* A `refresh_token` row is inserted into `users.refresh_tokens` with a 30-day expiry
* The `refresh_token` is set as an `HttpOnly` `Secure` cookie

#### SCENARIO 2: Invalid credentials return 401

**Scenario ID**: USER-BE-002.1-S2

**GIVEN**
* The password does not match the stored hash (or the email does not exist)

**WHEN**
* `POST /auth/login` is called

**THEN**
* Response is `401 Unauthorized` with `{"error": {"code": "INVALID_CREDENTIALS", "message": "..."}}`
* No token is issued; no timing difference leaks user existence

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../architecture/06-runtime-view.md)

---

### USER-BE-002.2 — POST /auth/refresh endpoint

AS A Users Service
I WANT to expose `POST /auth/refresh`
SO THAT clients can obtain a new access token without re-entering credentials

#### SCENARIO 1: Valid refresh token issues new access token

**Scenario ID**: USER-BE-002.2-S1

**GIVEN**
* The request carries a valid, non-expired `refresh_token` cookie

**WHEN**
* `POST /auth/refresh` is called

**THEN**
* A new RS256 JWT is returned with a fresh 15-minute expiry
* The old refresh token is rotated (invalidated and replaced)

#### SCENARIO 2: Expired or unknown refresh token rejected

**Scenario ID**: USER-BE-002.2-S2

**GIVEN**
* The refresh token is expired or not found in `users.refresh_tokens`

**WHEN**
* `POST /auth/refresh` is called

**THEN**
* Response is `401 Unauthorized` with error code `INVALID_REFRESH_TOKEN`

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

### USER-INFRA-002.1 — Users Service containerised and deployable

*Covered by USER-INFRA-001.1 — the same container serves all Users Service endpoints including `/auth/login` and `/auth/refresh`.*

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)

---

### USER-INFRA-002.2 — refresh_tokens table migration

AS AN operator
I WANT an Alembic migration that creates the `users.refresh_tokens` table
SO THAT the login flow can persist and rotate refresh tokens

#### SCENARIO 1: Migration creates refresh_tokens table

**Scenario ID**: USER-INFRA-002.2-S1

**GIVEN**
* The `users` schema exists (USER-INFRA-001.2 has run)

**WHEN**
* The migration for USER-STORY-002 is applied

**THEN**
* Table `users.refresh_tokens` exists with columns `(token_hash, user_id, expires_at, revoked)`
* A unique index on `token_hash` is present

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

### USER-INFRA-002.3 — Event handling

*Not applicable — login is a synchronous request/response flow; no async events are triggered.*

---

### USER-INFRA-002.4 — Monitoring and alarms for login endpoint

AS AN operator
I WANT an alert when the login error rate is elevated
SO THAT I can detect credential-stuffing attacks or service degradation early

#### SCENARIO 1: Alert fires on sustained 401 spike

**Scenario ID**: USER-INFRA-002.4-S1

**GIVEN**
* Prometheus scrapes `/metrics` on the Users Service

**WHEN**
* The rate of `401` responses on `POST /auth/login` exceeds 1% of total requests for 5 consecutive minutes

**THEN**
* An alert fires and is routed to the on-call channel

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

## USER-STORY-003 — View and edit own profile ✅ [Supporting]

AS A logged-in user
I WANT to view and update my profile (display name, bio, avatar)
SO THAT other users see accurate information about me

### SCENARIO 1: View own profile

**Scenario ID**: USER-STORY-003-S1

**GIVEN**
* The user is authenticated

**WHEN**
* The user navigates to their profile page

**THEN**
* Their current username, display name, bio, and avatar are displayed

### SCENARIO 2: Successful profile update

**Scenario ID**: USER-STORY-003-S2

**GIVEN**
* The user submits a valid updated display name and/or bio

**WHEN**
* `PATCH /users/me` is called

**THEN**
* The `users` row is updated
* The API returns `200 OK` with the updated profile

### SCENARIO 3: Avatar upload accepted

**Scenario ID**: USER-STORY-003-S3

**GIVEN**
* The user uploads an image file ≤2 MB in JPEG or PNG format

**WHEN**
* The avatar is submitted

**THEN**
* The image is stored and `avatar_url` is updated on the user record
* The API returns `200 OK` with the new `avatar_url`

### SCENARIO 4: Oversized avatar rejected

**Scenario ID**: USER-STORY-003-S4

**GIVEN**
* The user uploads a file larger than 2 MB

**WHEN**
* The request reaches the Users Service

**THEN**
* The API returns `422 Unprocessable Entity` with error code `AVATAR_TOO_LARGE`

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-FE-003.1 — Profile page

AS A logged-in user
I WANT a profile page showing my avatar, display name, bio, and follower counts
SO THAT I can review how my profile appears to others

#### SCENARIO 1: Profile page renders current data

**Scenario ID**: USER-FE-003.1-S1

**GIVEN**
* The user navigates to `/profile`

**WHEN**
* The page mounts

**THEN**
* `GET /users/me` is called and the response populates avatar, display name, bio, follower count, and followee count

**Architecture reference**: [Chapter 3 — Context and Scope](../architecture/03-context-and-scope.md)

---

### USER-FE-003.2 — Edit profile form

AS A logged-in user
I WANT an inline edit form on my profile page
SO THAT I can update my details without navigating away

#### SCENARIO 1: Edits saved and reflected immediately

**Scenario ID**: USER-FE-003.2-S1

**GIVEN**
* The user clicks "Edit profile" and modifies display name or bio

**WHEN**
* The user clicks "Save"

**THEN**
* `PATCH /users/me` is called with the changed fields
* On `200 OK` the profile page reflects the new values without a full reload

#### SCENARIO 2: Avatar preview before upload

**Scenario ID**: USER-FE-003.2-S2

**GIVEN**
* The user selects an image file via the avatar picker

**WHEN**
* The file is selected

**THEN**
* A local preview of the image is shown before the upload is submitted

**Architecture reference**: [Chapter 3 — Context and Scope](../architecture/03-context-and-scope.md)

---

### USER-BE-003.1 — GET /users/me and GET /users/{id} endpoints

AS A Users Service
I WANT to expose `GET /users/me` and `GET /users/{id}`
SO THAT the authenticated user can fetch their own profile and other services can resolve any user

#### SCENARIO 1: Own profile returned

**Scenario ID**: USER-BE-003.1-S1

**GIVEN**
* The request carries a valid JWT

**WHEN**
* `GET /users/me` is called

**THEN**
* Response is `200 OK` with `{id, username, display_name, bio, avatar_url, created_at}`

#### SCENARIO 2: Public profile returned by ID

**Scenario ID**: USER-BE-003.1-S2

**GIVEN**
* `{id}` matches an existing user

**WHEN**
* `GET /users/{id}` is called (used by Posts and Messaging Services)

**THEN**
* Response is `200 OK` with public fields `{id, username, display_name, avatar_url}`

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-BE-003.2 — PATCH /users/me endpoint

AS A Users Service
I WANT to expose `PATCH /users/me`
SO THAT authenticated users can update their profile fields

#### SCENARIO 1: Partial update applied

**Scenario ID**: USER-BE-003.2-S1

**GIVEN**
* The request carries a valid JWT and a body with one or more of `{display_name, bio, avatar_url}`

**WHEN**
* `PATCH /users/me` is called

**THEN**
* Only the supplied fields are updated in `users.users`
* Response is `200 OK` with the full updated profile

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-INFRA-003.1 — Users Service containerised and deployable

*Covered by USER-INFRA-001.1.*

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)

---

### USER-INFRA-003.2 — Profile fields migration

AS AN operator
I WANT an Alembic migration that adds `display_name`, `bio`, and `avatar_url` columns to `users.users`
SO THAT profile data can be stored and updated

#### SCENARIO 1: Migration adds profile columns

**Scenario ID**: USER-INFRA-003.2-S1

**GIVEN**
* The `users.users` table exists (USER-INFRA-001.2 has run)

**WHEN**
* The migration for USER-STORY-003 is applied

**THEN**
* Columns `display_name VARCHAR(100)`, `bio VARCHAR(300)`, and `avatar_url TEXT` exist on `users.users`
* Existing rows have `NULL` for the new columns (no data loss)

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)

---

### USER-INFRA-003.3 — Event handling

*Not applicable — profile updates are synchronous; no async events are triggered.*

---

### USER-INFRA-003.4 — Monitoring

*Covered by USER-INFRA-001.4 — the existing error-rate alert covers all Users Service endpoints.*

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)

---

## USER-STORY-004 — Follow / unfollow another user ✅ [Supporting]

AS A logged-in user
I WANT to follow or unfollow another user
SO THAT their posts appear in (or are removed from) my timeline feed

### SCENARIO 1: Successfully follow a user

**Scenario ID**: USER-STORY-004-S1

**GIVEN**
* The authenticated user is not already following the target user
* The target user exists

**WHEN**
* The user submits a follow request for the target

**THEN**
* A follow relationship is recorded in the `users` schema
* The response confirms the follow was created

### SCENARIO 2: Successfully unfollow a user

**Scenario ID**: USER-STORY-004-S2

**GIVEN**
* The authenticated user is currently following the target user

**WHEN**
* The user submits an unfollow request for the target

**THEN**
* The follow relationship is removed from the `users` schema
* The response confirms the unfollow

### SCENARIO 3: Follow non-existent user rejected

**Scenario ID**: USER-STORY-004-S3

**GIVEN**
* The target user ID does not exist

**WHEN**
* A follow request is submitted for that ID

**THEN**
* The API returns `404 Not Found` with error code `USER_NOT_FOUND`

### SCENARIO 4: Self-follow rejected

**Scenario ID**: USER-STORY-004-S4

**GIVEN**
* The authenticated user submits a follow request where the target ID equals their own ID

**WHEN**
* The request reaches the Users Service

**THEN**
* The API returns `422 Unprocessable Entity` with error code `CANNOT_FOLLOW_SELF`

**Architecture reference**: [Chapter 1 — Introduction and Goals](../architecture/01-introduction-and-goals.md), [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-FE-004.1 — Follow / unfollow button on user profile

AS A logged-in user
I WANT a Follow / Unfollow toggle button on another user's profile page
SO THAT I can manage my follow relationships without leaving the page

#### SCENARIO 1: Follow button triggers follow and updates to Unfollow

**Scenario ID**: USER-FE-004.1-S1

**GIVEN**
* The authenticated user is viewing a profile they do not follow
* The page shows a "Follow" button

**WHEN**
* The user clicks "Follow"

**THEN**
* A `POST /users/{id}/follow` request is sent with the Bearer JWT
* On success the button label changes to "Unfollow" without a full page reload

#### SCENARIO 2: Unfollow button triggers unfollow and updates to Follow

**Scenario ID**: USER-FE-004.1-S2

**GIVEN**
* The authenticated user is viewing a profile they already follow
* The page shows an "Unfollow" button

**WHEN**
* The user clicks "Unfollow"

**THEN**
* A `DELETE /users/{id}/follow` request is sent
* On success the button label changes to "Follow"

**Architecture reference**: [Chapter 3 — Context and Scope](../architecture/03-context-and-scope.md)

---

### USER-BE-004.1 — POST /users/{id}/follow endpoint

AS A Users Service
I WANT to expose `POST /users/{id}/follow`
SO THAT authenticated users can follow another user

#### SCENARIO 1: Follow relationship created

**Scenario ID**: USER-BE-004.1-S1

**GIVEN**
* The request carries a valid JWT
* The target `{id}` exists and is not the caller's own ID
* No existing follow relationship exists between caller and target

**WHEN**
* `POST /users/{id}/follow` is called

**THEN**
* A row is inserted into `users.follows (follower_id, followee_id, created_at)`
* Response is `201 Created` with `{follower_id, followee_id}`

#### SCENARIO 2: Duplicate follow is idempotent

**Scenario ID**: USER-BE-004.1-S2

**GIVEN**
* The follow relationship already exists

**WHEN**
* `POST /users/{id}/follow` is called again

**THEN**
* Response is `200 OK` (no error, no duplicate row)

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-BE-004.2 — DELETE /users/{id}/follow endpoint

AS A Users Service
I WANT to expose `DELETE /users/{id}/follow`
SO THAT authenticated users can unfollow another user

#### SCENARIO 1: Follow relationship removed

**Scenario ID**: USER-BE-004.2-S1

**GIVEN**
* The request carries a valid JWT
* A follow relationship exists between caller and target

**WHEN**
* `DELETE /users/{id}/follow` is called

**THEN**
* The row is deleted from `users.follows`
* Response is `204 No Content`

#### SCENARIO 2: Unfollow when not following is idempotent

**Scenario ID**: USER-BE-004.2-S2

**GIVEN**
* No follow relationship exists between caller and target

**WHEN**
* `DELETE /users/{id}/follow` is called

**THEN**
* Response is `204 No Content` (no error)

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-INFRA-004.1 — Users Service containerised and deployable

*Covered by USER-INFRA-001.1 — the same container serves all Users Service endpoints including follow/unfollow.*

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)

---

### USER-INFRA-004.2 — follows table migration

AS AN operator
I WANT an Alembic migration that creates the `users.follows` table
SO THAT follow relationships are persisted and queryable by the Posts Service feed

#### SCENARIO 1: Migration creates follows table

**Scenario ID**: USER-INFRA-004.2-S1

**GIVEN**
* The `users` schema exists (USER-INFRA-001.2 has run)

**WHEN**
* The migration for USER-STORY-004 is applied

**THEN**
* Table `users.follows` exists with columns `(follower_id, followee_id, created_at)`
* A composite primary key on `(follower_id, followee_id)` prevents duplicates
* Foreign keys reference `users.users(id)` for both columns

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md), [Chapter 9 — Architecture Decisions](../architecture/09-architecture-decisions.md)

---

### USER-INFRA-004.3 — Event handling

*Not applicable — follow/unfollow is a synchronous operation; no async events are required at this stage. If follower-count notifications are added later, this sub-story should be revisited.*

---

### USER-INFRA-004.4 — Monitoring and alarms for follow endpoints

AS AN operator
I WANT the follow/unfollow endpoints covered by the existing Users Service health check and error-rate alert
SO THAT degradation in the social graph is detected automatically

#### SCENARIO 1: Error-rate alert covers follow endpoints

**Scenario ID**: USER-INFRA-004.4-S1

**GIVEN**
* The Prometheus `/metrics` endpoint is scraped on the Users Service

**WHEN**
* The HTTP 5xx error rate across all Users Service endpoints (including `/users/{id}/follow`) exceeds 1% for 5 consecutive minutes

**THEN**
* The alert defined in USER-INFRA-001.4 fires

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../architecture/08-cross-cutting-concepts.md)

---

## USER-STORY-005 — List followers / followees ✅ [Supporting]

AS A logged-in user
I WANT to see who follows me and who I follow
SO THAT I can manage my social graph

### SCENARIO 1: View own followers list

**Scenario ID**: USER-STORY-005-S1

**GIVEN**
* The authenticated user has at least one follower

**WHEN**
* The user navigates to their followers list

**THEN**
* A paginated list of users who follow them is returned, each with `id`, `username`, and `avatar_url`

### SCENARIO 2: View own followees list

**Scenario ID**: USER-STORY-005-S2

**GIVEN**
* The authenticated user follows at least one user

**WHEN**
* The user navigates to their following list

**THEN**
* A paginated list of users they follow is returned

### SCENARIO 3: View another user's followers list

**Scenario ID**: USER-STORY-005-S3

**GIVEN**
* The authenticated user views another user's profile

**WHEN**
* The user clicks the followers count

**THEN**
* A paginated list of that user's followers is returned

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-FE-005.1 — Followers / following lists on profile page

AS A logged-in user
I WANT clickable follower and following counts on any profile page
SO THAT I can browse the social graph

#### SCENARIO 1: Clicking follower count opens followers list

**Scenario ID**: USER-FE-005.1-S1

**GIVEN**
* The user is on a profile page showing a follower count

**WHEN**
* The user clicks the follower count

**THEN**
* A modal or page opens showing the paginated followers list fetched from `GET /users/{id}/followers`

**Architecture reference**: [Chapter 3 — Context and Scope](../architecture/03-context-and-scope.md)

---

### USER-BE-005.1 — GET /users/{id}/followers and /followees endpoints

AS A Users Service
I WANT to expose `GET /users/{id}/followers` and `GET /users/{id}/followees`
SO THAT authenticated callers can retrieve the social graph for a given user

#### SCENARIO 1: Followers list returned paginated

**Scenario ID**: USER-BE-005.1-S1

**GIVEN**
* `{id}` is a valid user ID

**WHEN**
* `GET /users/{id}/followers?page=1&page_size=20` is called

**THEN**
* Response is `200 OK` with `{items: [{id, username, avatar_url}], page, page_size, has_next}`

#### SCENARIO 2: Candidate followees contract for Posts Service feed

**Scenario ID**: USER-BE-005.1-S2

**GIVEN**
* The Posts Service needs the list of accounts followed by `{id}` to build the feed query
* `GET /users/{id}/followees` is treated here as a candidate cross-context contract, pending architecture alignment

**WHEN**
* The contract is defined and the endpoint is called with a valid JWT

**THEN**
* The endpoint returns `200 OK` with the list of followee IDs and public profiles
* Until Chapter 5 documents this interface, this scenario is a to-be-defined dependency rather than an approved cross-context API

**Architecture reference**: [Chapter 5 — Building Block View](../architecture/05-building-block-view.md)

---

### USER-INFRA-005.1 — Users Service containerised and deployable

*Covered by USER-INFRA-001.1.*

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)

---

### USER-INFRA-005.2 — Data store

*Covered by USER-INFRA-004.2 — the `users.follows` table created for USER-STORY-004 is the data store for follower/followee queries. No additional migration required.*

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)

---

### USER-INFRA-005.3 — Event handling

*Not applicable — listing followers/followees is a synchronous read.*

---

### USER-INFRA-005.4 — Monitoring

*Covered by USER-INFRA-001.4.*

**Architecture reference**: [Chapter 7 — Deployment View](../architecture/07-deployment-view.md)
