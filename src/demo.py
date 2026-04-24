"""Scripted end-to-end walkthrough of the kata's three bounded contexts.

Runs the real services against in-memory repositories and prints each step
with its originating Story/Scenario ID so the mapping to tests is visible.
"""

from src.messaging.repository import (
    InMemoryConversationRepository,
    InMemoryMentionRepository,
    InMemoryMessageRepository,
)
from src.messaging.service import MessagingService
from src.posts.follow_repository import InMemoryFollowRepository
from src.posts.repository import InMemoryPostRepository
from src.posts.service import PostService
from src.posts.timeline_service import TimelineService
from src.users.exceptions import AvatarTooLargeError, EmailAlreadyExistsError
from src.users.repository import InMemoryUserRepository
from src.users.service import UserService


def section(title: str) -> None:
    print(f"\n=== {title} ===")


def main() -> None:
    user_service = UserService(InMemoryUserRepository())
    messaging = MessagingService(
        conversations=InMemoryConversationRepository(),
        messages=InMemoryMessageRepository(),
        users=user_service,
        mentions=InMemoryMentionRepository(),
    )
    posts = PostService(InMemoryPostRepository())
    follows = InMemoryFollowRepository()
    timeline = TimelineService(posts._repo, follows)

    print("Social Network Kata — scripted demo")
    print("Each step references the user story and scenario it exercises.")

    section("USER-STORY-001 · register two accounts")
    alice = user_service.register("alice@example.com", "alice", "s3cret-pass")
    bob = user_service.register("bob@example.com", "bob", "s3cret-pass")
    print(f"  registered alice  id={alice.id[:8]}…  username={alice.username}")
    print(f"  registered bob    id={bob.id[:8]}…  username={bob.username}")

    section("USER-STORY-001-S2 · duplicate email rejected")
    try:
        user_service.register("alice@example.com", "alice2", "s3cret-pass")
    except EmailAlreadyExistsError as exc:
        print(f"  registration refused: {exc}")

    section("USER-STORY-002 · alice logs in")
    session = user_service.login("alice@example.com", "s3cret-pass")
    print(f"  access_token  = {session.access_token[:16]}…")
    print(f"  refresh_token = {session.refresh_token[:16]}…")

    section("USER-STORY-003 · alice updates her profile")
    user_service.update_profile(
        alice.id, display_name="Alice A.", bio="likes pair programming"
    )
    profile = user_service.get_profile(alice.id)
    print(f"  display_name = {profile.display_name!r}")
    print(f"  bio          = {profile.bio!r}")

    section("USER-STORY-003-S3 · alice uploads a small avatar")
    png_bytes = b"\x89PNG\r\n\x1a\n" + b"x" * 1024
    user_service.upload_avatar(alice.id, png_bytes, "image/png")
    print(f"  avatar_url = {user_service.get_profile(alice.id).avatar_url}")

    section("USER-STORY-003-S4 · oversized avatar rejected (limit 2 MB)")
    try:
        user_service.upload_avatar(alice.id, b"x" * (2 * 1024 * 1024 + 1), "image/png")
    except AvatarTooLargeError as exc:
        print(f"  upload refused: {exc}")

    section("MSG-STORY-001 · alice starts a conversation and sends a message")
    conversation = messaging.start_conversation(alice.id, bob.id)
    first = messaging.send_message(
        sender_id=alice.id,
        conversation_id=conversation.id,
        text="hi bob — ready to pair?",
    )
    print(f"  conversation_id = {conversation.id[:8]}…")
    print(f'  alice -> bob    : "{first.text}"')

    section("MSG-STORY-003 · alice sends a message that mentions @bob")
    mention_msg = messaging.send_message(
        sender_id=alice.id,
        conversation_id=conversation.id,
        text="hey @bob how are you",
    )
    stored = messaging._mentions.find_by_message(mention_msg.id)
    print(f'  alice -> bob    : "{mention_msg.text}"')
    print(
        f"  mention stored  : message={mention_msg.id[:8]}… "
        f"target={stored[0].target_user_id[:8]}… (resolved from @bob)"
    )

    section("MSG-STORY-003-S2 · unknown handle silently ignored")
    ghost_msg = messaging.send_message(
        sender_id=alice.id,
        conversation_id=conversation.id,
        text="hey @ghostuser nobody home",
    )
    ghost_mentions = messaging._mentions.find_by_message(ghost_msg.id)
    print(f'  alice -> bob    : "{ghost_msg.text}"')
    print(f"  mentions stored : {len(ghost_mentions)} (message saved normally)")

    section("MSG-STORY-002 · bob reads the conversation")
    page = messaging.get_messages(bob.id, conversation.id)
    for msg in page["items"]:
        who = "alice" if msg.sender_id == alice.id else "bob"
        print(f"  [{msg.created_at:%H:%M:%S}] {who}: {msg.text}")

    section("POST-STORY-001 · alice creates a post")
    post = posts.create_post(alice.id, "first post from the kata demo")
    print(f'  posted by alice : "{post.text}"')

    section("POST-STORY-002 · bob follows alice and reads his timeline")
    follows.add_follow(bob.id, alice.id)
    bob_timeline = timeline.get_timeline(bob.id)
    for p in bob_timeline.items:
        print(f'  [{p.created_at:%H:%M:%S}] alice: "{p.text}"')

    print("\nDemo complete. Run `docker run --rm <image> pytest tests/ -v` for tests.")


if __name__ == "__main__":
    main()
