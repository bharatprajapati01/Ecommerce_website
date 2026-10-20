from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse

from .models import Comment, Follow, Like, Post


class SocialFlowTests(TestCase):
    def setUp(self):
        self.alice = User.objects.create_user("alice", password="pw12345!x")
        self.bob = User.objects.create_user("bob", password="pw12345!x")
        self.client.login(username="alice", password="pw12345!x")

    def test_profile_auto_created(self):
        self.assertTrue(hasattr(self.alice, "profile"))

    def test_login_required(self):
        self.client.logout()
        r = self.client.get(reverse("feed"))
        self.assertEqual(r.status_code, 302)

    def test_signup_creates_user_and_logs_in(self):
        self.client.logout()
        r = self.client.post(
            reverse("signup"),
            {"username": "carol", "password1": "Str0ng-pass!9", "password2": "Str0ng-pass!9"},
        )
        self.assertRedirects(r, reverse("feed"))
        self.assertTrue(User.objects.filter(username="carol").exists())

    def test_create_post_and_see_in_feed(self):
        self.client.post(reverse("feed"), {"content": "hello world"})
        self.assertEqual(Post.objects.count(), 1)
        r = self.client.get(reverse("feed"))
        self.assertContains(r, "hello world")

    def test_feed_only_shows_followed_users(self):
        Post.objects.create(author=self.bob, content="bob secret post")
        self.assertNotContains(self.client.get(reverse("feed")), "bob secret post")
        self.client.post(reverse("toggle_follow", args=["bob"]))
        self.assertContains(self.client.get(reverse("feed")), "bob secret post")
        self.assertContains(self.client.get(reverse("feed") + "?scope=all"), "bob secret post")

    def test_comment(self):
        p = Post.objects.create(author=self.bob, content="x")
        self.client.post(reverse("post_detail", args=[p.id]), {"content": "nice!"})
        self.assertEqual(Comment.objects.filter(post=p, author=self.alice).count(), 1)
        self.assertContains(self.client.get(reverse("post_detail", args=[p.id])), "nice!")

    def test_like_toggle(self):
        p = Post.objects.create(author=self.bob, content="x")
        r = self.client.post(reverse("toggle_like", args=[p.id]))
        self.assertEqual(r.json(), {"liked": True, "count": 1})
        r = self.client.post(reverse("toggle_like", args=[p.id]))
        self.assertEqual(r.json(), {"liked": False, "count": 0})
        self.assertEqual(Like.objects.count(), 0)

    def test_follow_toggle_and_self_follow_blocked(self):
        r = self.client.post(reverse("toggle_follow", args=["bob"]))
        self.assertEqual(r.json(), {"following": True, "followers": 1})
        r = self.client.post(reverse("toggle_follow", args=["bob"]))
        self.assertEqual(r.json(), {"following": False, "followers": 0})
        r = self.client.post(reverse("toggle_follow", args=["alice"]))
        self.assertEqual(r.status_code, 400)
        self.assertEqual(Follow.objects.count(), 0)

    def test_like_and_follow_require_post(self):
        p = Post.objects.create(author=self.bob, content="x")
        self.assertEqual(self.client.get(reverse("toggle_like", args=[p.id])).status_code, 405)
        self.assertEqual(self.client.get(reverse("toggle_follow", args=["bob"])).status_code, 405)

    def test_cannot_delete_others_post(self):
        p = Post.objects.create(author=self.bob, content="x")
        r = self.client.post(reverse("delete_post", args=[p.id]))
        self.assertEqual(r.status_code, 404)
        self.assertTrue(Post.objects.filter(id=p.id).exists())

    def test_profile_and_lists_and_search(self):
        Follow.objects.create(follower=self.alice, following=self.bob)
        self.assertContains(self.client.get(reverse("profile", args=["bob"])), "followers")
        self.assertContains(self.client.get(reverse("follow_list", args=["bob", "followers"])), "alice")
        self.assertContains(self.client.get(reverse("search") + "?q=bo"), "bob")

    def test_edit_profile_bio(self):
        self.client.post(reverse("edit_profile"), {"bio": "I like code"})
        self.alice.profile.refresh_from_db()
        self.assertEqual(self.alice.profile.bio, "I like code")


class CategoryTests(TestCase):
    def setUp(self):
        from .models import Category

        self.alice = User.objects.create_user("alice", password="pw12345!x")
        self.client.login(username="alice", password="pw12345!x")
        self.Category = Category

    def test_seeded_categories_have_subcategories(self):
        music = self.Category.objects.get(slug="music")
        self.assertIsNone(music.parent)
        self.assertTrue(music.children.filter(name="Pop").exists())
        self.assertEqual(self.Category.objects.filter(parent__isnull=True).count(), 6)

    def test_post_with_subcategory(self):
        pop = self.Category.objects.get(slug="music-pop")
        self.client.post(reverse("feed"), {"content": "new album out", "category": pop.id})
        post = Post.objects.get()
        self.assertEqual(post.category, pop)
        self.assertEqual(str(post.category), "Music › Pop")

    def test_filter_by_parent_includes_subcategory_posts(self):
        pop = self.Category.objects.get(slug="music-pop")
        pc = self.Category.objects.get(slug="gaming-pc")
        Post.objects.create(author=self.alice, content="pop post", category=pop)
        Post.objects.create(author=self.alice, content="pc post", category=pc)
        r = self.client.get(reverse("feed") + "?category=music")
        self.assertContains(r, "pop post")
        self.assertNotContains(r, "pc post")
        r = self.client.get(reverse("feed") + "?category=gaming-pc")
        self.assertContains(r, "pc post")
        self.assertNotContains(r, "pop post")

    def test_category_browse_defaults_to_everyone(self):
        bob = User.objects.create_user("bob", password="pw12345!x")
        pop = self.Category.objects.get(slug="music-pop")
        Post.objects.create(author=bob, content="bob pop post", category=pop)
        # alice does not follow bob, but browsing a category shows everyone
        self.assertContains(self.client.get(reverse("feed") + "?category=music-pop"), "bob pop post")

    def test_unknown_category_slug_is_ignored(self):
        self.assertEqual(self.client.get(reverse("feed") + "?category=nope").status_code, 200)


class EngagementTests(TestCase):
    """Notifications, messages, saved posts, activity, password change and the nav badges."""

    def setUp(self):
        from .models import Bookmark, Message, Notification

        self.Bookmark, self.Message, self.Notification = Bookmark, Message, Notification
        self.alice = User.objects.create_user("alice", password="pw12345!x")
        self.bob = User.objects.create_user("bob", password="pw12345!x")
        self.post = Post.objects.create(author=self.bob, content="bob's post")
        self.client.login(username="alice", password="pw12345!x")

    # ---- notifications
    def test_like_notifies_author_and_unlike_removes_it(self):
        self.client.post(reverse("toggle_like", args=[self.post.id]))
        n = self.Notification.objects.get()
        self.assertEqual((n.recipient, n.actor, n.kind), (self.bob, self.alice, "like"))
        self.client.post(reverse("toggle_like", args=[self.post.id]))
        self.assertEqual(self.Notification.objects.count(), 0)

    def test_no_notification_for_your_own_actions(self):
        mine = Post.objects.create(author=self.alice, content="mine")
        self.client.post(reverse("toggle_like", args=[mine.id]))
        self.client.post(reverse("post_detail", args=[mine.id]), {"content": "me again"})
        self.assertEqual(self.Notification.objects.count(), 0)

    def test_comment_and_follow_notify(self):
        self.client.post(reverse("post_detail", args=[self.post.id]), {"content": "nice"})
        self.client.post(reverse("toggle_follow", args=["bob"]))
        kinds = set(self.Notification.objects.filter(recipient=self.bob).values_list("kind", flat=True))
        self.assertEqual(kinds, {"comment", "follow"})
        self.client.post(reverse("toggle_follow", args=["bob"]))  # unfollow
        self.assertFalse(self.Notification.objects.filter(kind="follow").exists())

    def test_notifications_page_shows_badge_then_marks_read(self):
        self.client.post(reverse("toggle_like", args=[self.post.id]))
        self.client.logout()
        self.client.login(username="bob", password="pw12345!x")
        self.assertContains(self.client.get(reverse("feed")), 'class="badge">1<')
        r = self.client.get(reverse("notifications"))
        self.assertContains(r, "alice")
        self.assertContains(r, "liked your post")
        self.assertNotContains(self.client.get(reverse("feed")), 'class="badge">1<')

    # ---- messages
    def test_send_message_unread_badge_and_mark_read(self):
        self.client.post(reverse("thread", args=["bob"]), {"body": "hi bob"})
        self.assertEqual(self.Message.objects.get().body, "hi bob")
        self.client.logout()
        self.client.login(username="bob", password="pw12345!x")
        self.assertContains(self.client.get(reverse("inbox")), 'class="badge">1<')
        r = self.client.get(reverse("thread", args=["alice"]))
        self.assertContains(r, "hi bob")
        self.assertEqual(self.Message.objects.filter(is_read=False).count(), 0)
        self.assertContains(self.client.get(reverse("inbox")), "alice")

    def test_message_edge_cases(self):
        self.client.post(reverse("thread", args=["bob"]), {"body": "   "})
        self.assertEqual(self.Message.objects.count(), 0)
        self.assertRedirects(self.client.get(reverse("thread", args=["alice"])), reverse("inbox"))
        self.assertEqual(self.client.get(reverse("thread", args=["nobody"])).status_code, 404)

    # ---- saved posts
    def test_save_toggle_and_saved_page(self):
        r = self.client.post(reverse("toggle_bookmark", args=[self.post.id]))
        self.assertEqual(r.json(), {"saved": True})
        self.assertContains(self.client.get(reverse("saved")), "bob&#x27;s post")
        r = self.client.post(reverse("toggle_bookmark", args=[self.post.id]))
        self.assertEqual(r.json(), {"saved": False})
        self.assertNotContains(self.client.get(reverse("saved")), "bob&#x27;s post")
        self.assertEqual(self.client.get(reverse("toggle_bookmark", args=[self.post.id])).status_code, 405)

    # ---- activity, settings, menu
    def test_activity_page_counts(self):
        self.client.post(reverse("toggle_like", args=[self.post.id]))
        self.client.post(reverse("post_detail", args=[self.post.id]), {"content": "great"})
        r = self.client.get(reverse("activity"))
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.context["counts"], {"posts": 0, "likes": 1, "comments": 1, "saved": 0})

    def test_change_password(self):
        r = self.client.post(
            reverse("password_change"),
            {"old_password": "pw12345!x", "new_password1": "Br4nd-new-pass!", "new_password2": "Br4nd-new-pass!"},
        )
        self.assertRedirects(r, reverse("edit_profile"))
        self.alice.refresh_from_db()
        self.assertTrue(self.alice.check_password("Br4nd-new-pass!"))

    def test_more_menu_and_nav_links_present(self):
        html = self.client.get(reverse("feed")).content.decode()
        for needle in ("Settings", "Your activity", "Saved", "Switch appearance", "Log out", "Messages", "Notifications"):
            self.assertIn(needle, html)

    def test_new_pages_require_login(self):
        self.client.logout()
        for name in ("inbox", "notifications", "saved", "activity", "password_change"):
            self.assertEqual(self.client.get(reverse(name)).status_code, 302, name)
