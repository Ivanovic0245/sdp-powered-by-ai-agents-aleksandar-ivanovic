# Messaging Domain — Story Bundles

---

## MSG-STORY-001 — Send a direct message ✅ [Supporting]

AS A logged-in user
I WANT to send a direct message to another user
SO THAT I can have private conversations on the platform

### SCENARIO 1: Successful message sent in existing conversation

**Scenario ID**: MSG-STORY-001-S1

**GIVEN**
* The authenticated user has an existing conversation with the recipient
* The message text is non-empty

**WHEN**
* The user submits a message in that conversation

**THEN**
* The message is persisted in the `messaging` schema
* The API returns `201 Created` with the new message object

### SCENARIO 2: Message sent creates new conversation

**Scenario ID**: MSG-STORY-001-S2

**GIVEN**
* No conversation exists between the sender and recipient
* The recipient exists in the Users Service

**WHEN**
* The user sends a message to the recipient for the first time

**THEN**
* A new conversation record is created
* The message is persisted within that conversation
* The API returns `201 Created` with the message and `conversation_id`

### SCENARIO 3: Message to non-existent recipient rejected

**Scenario ID**: MSG-STORY-001-S3

**GIVEN**
* The recipient user ID does not exist in the Users Service

**WHEN**
* The user attempts to send a message to that ID

**THEN**
* The API returns `404 Not Found` with error code `USER_NOT_FOUND`
* No message or conversation is created

### SCENARIO 4: Empty message rejected

**Scenario ID**: MSG-STORY-001-S4

**GIVEN**
* The user submits a message with empty or whitespace-only text

**WHEN**
* The request reaches the Messaging Service

**THEN**
* The API returns `422 Unprocessable Entity` with error code `MESSAGE_TEXT_REQUIRED`

### SCENARIO 5: Unauthenticated request rejected

**Scenario ID**: MSG-STORY-001-S5

**GIVEN**
* The request carries no JWT or an expired JWT

**WHEN**
* `POST /conversations/{id}/messages` is called

**THEN**
* The API returns `401 Unauthorized`

**Architecture reference**: [Chapter 1 — Introduction and Goals](../../architecture/01-introduction-and-goals.md), [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md)

---

### MSG-FE-001.1 — Conversation and message compose UI

AS A logged-in user
I WANT a conversation view with a message input at the bottom
SO THAT I can read and send messages in a single screen

#### SCENARIO 1: Sending a message appends it to the conversation

**Scenario ID**: MSG-FE-001.1-S1

**GIVEN**
* The user is viewing a conversation at `/conversations/{id}`
* The message input contains non-empty text

**WHEN**
* The user clicks "Send" or presses Enter

**THEN**
* A `POST /conversations/{id}/messages` request is sent with the Bearer JWT
* On `201 Created` the new message is appended to the conversation view
* The input field is cleared

#### SCENARIO 2: Starting a new conversation from a user profile

**Scenario ID**: MSG-FE-001.1-S2

**GIVEN**
* The user is viewing another user's profile

**WHEN**
* The user clicks "Message"

**THEN**
* A `POST /conversations` request is sent with `{recipient_id}`
* The user is navigated to the new or existing conversation view

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md)

---

### MSG-FE-001.2 — Message input validation

AS A logged-in user
I WANT the message input to prevent empty submissions
SO THAT I cannot accidentally send blank messages

#### SCENARIO 1: Send button disabled when input is empty

**Scenario ID**: MSG-FE-001.2-S1

**GIVEN**
* The message input is empty or contains only whitespace

**WHEN**
* The compose area is rendered

**THEN**
* The "Send" button is disabled and cannot be clicked

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md)

---

### MSG-BE-001.1 — POST /conversations endpoint

AS A Messaging Service
I WANT to expose `POST /conversations`
SO THAT a conversation can be created or retrieved between two users

#### SCENARIO 1: New conversation created

**Scenario ID**: MSG-BE-001.1-S1

**GIVEN**
* The request carries a valid JWT
* The body contains `{recipient_id}` for a user that exists in the Users Service
* No conversation between sender and recipient exists

**WHEN**
* `POST /conversations` is called

**THEN**
* The Messaging Service calls `GET /users/{recipient_id}` to verify the recipient exists
* A row is inserted into `messaging.conversations`
* A row is inserted into `messaging.conversation_participants` for both users
* Response is `201 Created` with `{conversation_id, participants}`

#### SCENARIO 2: Existing conversation returned (idempotent)

**Scenario ID**: MSG-BE-001.1-S2

**GIVEN**
* A conversation between sender and recipient already exists

**WHEN**
* `POST /conversations` is called again with the same `recipient_id`

**THEN**
* No new conversation is created
* Response is `200 OK` with the existing `{conversation_id, participants}`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md)

---

### MSG-BE-001.2 — POST /conversations/{id}/messages endpoint

AS A Messaging Service
I WANT to expose `POST /conversations/{id}/messages`
SO THAT authenticated users can send messages within a conversation

#### SCENARIO 1: Message persisted and returned

**Scenario ID**: MSG-BE-001.2-S1

**GIVEN**
* The request carries a valid JWT
* The caller is a participant in conversation `{id}`
* The body contains `{text}` that is non-empty

**WHEN**
* `POST /conversations/{id}/messages` is called

**THEN**
* A row is inserted into `messaging.messages (id, conversation_id, sender_id, text, created_at)`
* Response is `201 Created` with `{id, conversation_id, sender_id, text, created_at}`

#### SCENARIO 2: Non-participant cannot send message

**Scenario ID**: MSG-BE-001.2-S2

**GIVEN**
* The authenticated user is not a participant in conversation `{id}`

**WHEN**
* `POST /conversations/{id}/messages` is called

**THEN**
* Response is `403 Forbidden` with error code `NOT_A_PARTICIPANT`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md)

---

### MSG-INFRA-001.1 — Messaging Service containerised and deployable

AS AN operator
I WANT the Messaging Service packaged as a Docker image
SO THAT it can be deployed independently behind the nginx reverse proxy

#### SCENARIO 1: Container starts and serves traffic

**Scenario ID**: MSG-INFRA-001.1-S1

**GIVEN**
* A Docker image is built from the Messaging Service source
* `DATABASE_URL` and `JWT_PUBLIC_KEY` are set as environment variables

**WHEN**
* The container starts

**THEN**
* The service is reachable on its configured port
* `GET /health` returns `200 OK`

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### MSG-INFRA-001.2 — Messaging schema migration

AS AN operator
I WANT an Alembic migration that creates the `messaging` schema tables
SO THAT the Messaging Service can persist conversations and messages

#### SCENARIO 1: Migration creates required tables

**Scenario ID**: MSG-INFRA-001.2-S1

**GIVEN**
* A PostgreSQL instance has no `messaging` schema tables

**WHEN**
* `alembic upgrade head` is run for the Messaging Service

**THEN**
* Tables `messaging.conversations`, `messaging.conversation_participants`, and `messaging.messages` exist
* `messaging.messages` has an index on `(conversation_id, created_at DESC)`
* Migration is idempotent

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md), [Chapter 9 — Architecture Decisions](../../architecture/09-architecture-decisions.md)

---

### MSG-INFRA-001.3 — Event handling

*Not applicable at this stage — message delivery is synchronous. If push notifications or unread-count events are added later, this sub-story should be revisited.*

---

### MSG-INFRA-001.4 — Monitoring and alarms for Messaging Service

AS AN operator
I WANT a health check endpoint and an error-rate alert on the Messaging Service
SO THAT I am notified when messaging is degraded

#### SCENARIO 1: Health check returns 200

**Scenario ID**: MSG-INFRA-001.4-S1

**GIVEN**
* The Messaging Service is running and connected to its database

**WHEN**
* `GET /health` is called

**THEN**
* Response is `200 OK` with `{"status": "ok"}`

#### SCENARIO 2: Alert fires on elevated error rate

**Scenario ID**: MSG-INFRA-001.4-S2

**GIVEN**
* Prometheus scrapes `/metrics` on the Messaging Service every 15 seconds

**WHEN**
* The HTTP 5xx error rate exceeds 1% for 5 consecutive minutes

**THEN**
* An alert fires and is routed to the on-call channel

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../../architecture/08-cross-cutting-concepts.md)

---

## MSG-STORY-002 — Read a conversation ✅ [Supporting]

AS A logged-in user
I WANT to open a conversation and read its message history
SO THAT I can follow the thread of a private exchange

### SCENARIO 1: Conversation messages returned in order

**Scenario ID**: MSG-STORY-002-S1

**GIVEN**
* The authenticated user is a participant in the conversation
* The conversation has at least one message

**WHEN**
* The user opens the conversation

**THEN**
* Messages are returned sorted by `created_at ASC`, paginated (default 50 per page)
* Each message includes `sender_id`, `text`, and `created_at`

### SCENARIO 2: Non-participant cannot read conversation

**Scenario ID**: MSG-STORY-002-S2

**GIVEN**
* The authenticated user is not a participant in the conversation

**WHEN**
* `GET /conversations/{id}/messages` is called

**THEN**
* The API returns `403 Forbidden` with error code `NOT_A_PARTICIPANT`

### SCENARIO 3: Conversation list shows all user conversations

**Scenario ID**: MSG-STORY-002-S3

**GIVEN**
* The authenticated user has one or more conversations

**WHEN**
* `GET /conversations` is called

**THEN**
* A list of conversations is returned, each with the other participant's profile and the latest message preview

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md)

---

### MSG-FE-002.1 — Conversations list and message thread view

AS A logged-in user
I WANT a conversations inbox and a message thread view
SO THAT I can navigate between conversations and read messages

#### SCENARIO 1: Inbox lists conversations with latest message preview

**Scenario ID**: MSG-FE-002.1-S1

**GIVEN**
* The user navigates to `/conversations`

**WHEN**
* The page mounts

**THEN**
* `GET /conversations` is called and each conversation is shown with the other participant's avatar, username, and latest message snippet

#### SCENARIO 2: Opening a conversation loads message history

**Scenario ID**: MSG-FE-002.1-S2

**GIVEN**
* The user clicks a conversation in the inbox

**WHEN**
* The conversation view opens

**THEN**
* `GET /conversations/{id}/messages` is called and messages are rendered oldest-first, scrolled to the bottom

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md)

---

### MSG-BE-002.1 — GET /conversations and GET /conversations/{id}/messages endpoints

AS A Messaging Service
I WANT to expose `GET /conversations` and `GET /conversations/{id}/messages`
SO THAT participants can list their conversations and read message history

#### SCENARIO 1: Conversations list returned

**Scenario ID**: MSG-BE-002.1-S1

**GIVEN**
* The request carries a valid JWT

**WHEN**
* `GET /conversations` is called

**THEN**
* Response is `200 OK` with conversations where the caller is a participant, each enriched with the other participant's public profile (via Users Service) and the latest message

#### SCENARIO 2: Message history returned paginated

**Scenario ID**: MSG-BE-002.1-S2

**GIVEN**
* The caller is a participant in conversation `{id}`

**WHEN**
* `GET /conversations/{id}/messages?page=1&page_size=50` is called

**THEN**
* Response is `200 OK` with `{items: [...], page, page_size, has_next}` sorted `created_at ASC`

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md)

---

### MSG-INFRA-002.1 — Messaging Service containerised and deployable

*Covered by MSG-INFRA-001.1.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### MSG-INFRA-002.2 — Data store

*Covered by MSG-INFRA-001.2 — the `messaging.messages` table and its index on `(conversation_id, created_at)` already support read queries.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### MSG-INFRA-002.3 — Event handling

*Not applicable — reading messages is a synchronous read.*

---

### MSG-INFRA-002.4 — Monitoring

*Covered by MSG-INFRA-001.4.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

## MSG-STORY-003 — Mention a user in a message ✅ [Supporting]

AS A logged-in user
I WANT to @mention another user in a message
SO THAT they are notified and can see the context of the mention

### SCENARIO 1: Mention detected and stored

**Scenario ID**: MSG-STORY-003-S1

**GIVEN**
* The message text contains `@username` for an existing user

**WHEN**
* The message is sent

**THEN**
* The Messaging Service resolves the username to a `user_id` via the Users Service
* A row is inserted into `messaging.mentions (message_id, target_user_id)`

### SCENARIO 2: Unknown @handle silently ignored

**Scenario ID**: MSG-STORY-003-S2

**GIVEN**
* The message text contains `@nonexistentuser`

**WHEN**
* The message is sent

**THEN**
* The message is saved normally
* No mention record is created for the unknown handle
* No error is returned to the sender

### SCENARIO 3: Multiple mentions in one message

**Scenario ID**: MSG-STORY-003-S3

**GIVEN**
* The message text contains two or more valid `@username` handles

**WHEN**
* The message is sent

**THEN**
* A mention record is created for each resolved user

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md)

---

### MSG-FE-003.1 — @mention autocomplete in message input

AS A logged-in user
I WANT an autocomplete dropdown when I type `@` in the message input
SO THAT I can mention users without knowing their exact handle

#### SCENARIO 1: Autocomplete appears on @ trigger

**Scenario ID**: MSG-FE-003.1-S1

**GIVEN**
* The user is typing in the message input

**WHEN**
* The user types `@` followed by at least one character

**THEN**
* A dropdown appears with matching usernames returned by the Users domain username search / handle resolution capability
* Selecting a suggestion inserts the full `@username` into the input

**Cross-domain dependency**: This scenario depends on the Users-domain handle resolution endpoint `GET /users?username={handle}` as documented in the runtime view; any future Users story inventory entry should align with that contract rather than redefining it here.

**Architecture reference**: [Chapter 3 — Context and Scope](../../architecture/03-context-and-scope.md); [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md)

---

### MSG-BE-003.1 — Mention detection and storage on message send

AS A Messaging Service
I WANT to parse `@username` handles from message text after a message is saved
SO THAT mentions are recorded for notification purposes

#### SCENARIO 1: Mention resolved and stored

**Scenario ID**: MSG-BE-003.1-S1

**GIVEN**
* The message text contains `@validuser`
* The Users domain can resolve `validuser` to a matching user

**WHEN**
* The message is persisted

**THEN**
* The Messaging Service calls the Users-domain handle-resolution contract for `validuser`
* A row is inserted into `messaging.mentions (message_id, target_user_id)`

#### SCENARIO 2: Mention resolution failure does not fail message send

**Scenario ID**: MSG-BE-003.1-S2

**GIVEN**
* The Users Service is unreachable during mention resolution

**WHEN**
* The message is sent with an `@handle`

**THEN**
* The message is saved successfully
* Mention resolution failure is logged with `trace_id`
* The sender receives `201 Created` (mention is best-effort)

**Architecture reference**: [Chapter 5 — Building Block View](../../architecture/05-building-block-view.md), [Chapter 6 — Runtime View](../../architecture/06-runtime-view.md), [Chapter 8 — Cross-Cutting Concepts](../../architecture/08-cross-cutting-concepts.md)

---

### MSG-INFRA-003.1 — Messaging Service containerised and deployable

*Covered by MSG-INFRA-001.1.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### MSG-INFRA-003.2 — mentions table migration

AS AN operator
I WANT an Alembic migration that creates the `messaging.mentions` table
SO THAT mention records can be persisted

#### SCENARIO 1: Migration creates mentions table

**Scenario ID**: MSG-INFRA-003.2-S1

**GIVEN**
* The `messaging` schema exists (MSG-INFRA-001.2 has run)

**WHEN**
* The migration for MSG-STORY-003 is applied

**THEN**
* Table `messaging.mentions` exists with columns `(id, message_id, target_user_id, created_at)`
* A foreign key from `message_id` to `messaging.messages(id)` with `ON DELETE CASCADE` exists

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)

---

### MSG-INFRA-003.3 — Event handling

AS AN operator
I WANT mention resolution to be fault-tolerant with respect to the Users Service
SO THAT a Users Service outage does not degrade message sending

#### SCENARIO 1: Mention resolution logged on failure without blocking response

**Scenario ID**: MSG-INFRA-003.3-S1

**GIVEN**
* The Users Service returns a non-2xx response or times out during mention resolution

**WHEN**
* The Messaging Service calls the Users handle-resolution contract for `{handle}`

**THEN**
* The error is caught, logged with `trace_id`, and the message send completes with `201 Created`
* No mention row is inserted for the unresolved handle

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md), [Chapter 8 — Cross-Cutting Concepts](../../architecture/08-cross-cutting-concepts.md)

---

### MSG-INFRA-003.4 — Monitoring

*Covered by MSG-INFRA-001.4.*

**Architecture reference**: [Chapter 7 — Deployment View](../../architecture/07-deployment-view.md)
