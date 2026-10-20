from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth import views as auth_views
from django.contrib.auth.models import User
from django.contrib.messages.views import SuccessMessageMixin
from django.core.paginator import Paginator
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import CommentForm, PostForm, ProfileForm, SignUpForm
from .models import Bookmark, Category, Comment, Follow, Like, Message, Notification, Post, notify


def signup(request):
    if request.user.is_authenticated:
        return redirect("feed")
    form = SignUpForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        return redirect("feed")
    return render(request, "social/signup.html", {"form": form})


def _annotate(posts, user):
    """Attach like/comment counts and whether the current user liked each post."""
    posts = posts.select_related("author", "author__profile", "category", "category__parent").annotate(
        like_count=Count("likes", distinct=True),
        comment_count=Count("comments", distinct=True),
    )
    liked_ids = set(Like.objects.filter(user=user).values_list("post_id", flat=True))
    saved_ids = set(Bookmark.objects.filter(user=user).values_list("post_id", flat=True))
    page_posts = list(posts)
    for p in page_posts:
        p.liked = p.id in liked_ids
        p.saved = p.id in saved_ids
    return page_posts


def _posts_in_order(ids, user):
    """Annotated posts in the same order as `ids` (so 'most recently liked first' is kept)."""
    by_id = {p.id: p for p in _annotate(Post.objects.filter(id__in=ids), user)}
    return [by_id[i] for i in ids if i in by_id]


@login_required
def feed(request):
    """Posts from people the user follows, plus their own. ?scope=all shows everyone."""
    active = None
    slug = request.GET.get("category", "").strip()
    if slug:
        active = Category.objects.select_related("parent").filter(slug=slug).first()
    # Browsing a category defaults to everyone's posts, not just people you follow.
    scope = request.GET.get("scope") or ("all" if active else "following")
    qs = Post.objects.all()
    if active:
        qs = qs.filter(Q(category=active) | Q(category__parent=active))
    if scope != "all":
        following_ids = list(request.user.following.values_list("following_id", flat=True))
        qs = qs.filter(Q(author_id__in=following_ids) | Q(author=request.user))

    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect("feed")
    else:
        form = PostForm()

    page = Paginator(qs, 10).get_page(request.GET.get("page"))
    page.object_list = _annotate(Post.objects.filter(id__in=[p.id for p in page.object_list]), request.user)
    suggestions = (
        User.objects.exclude(id=request.user.id)
        .exclude(followers__follower=request.user)
        .select_related("profile")[:5]
    )
    return render(
        request,
        "social/feed.html",
        {
            "page": page,
            "form": form,
            "scope": scope,
            "suggestions": suggestions,
            "categories": Category.objects.filter(parent__isnull=True).prefetch_related("children"),
            "active_category": active,
            "open_id": (active.parent_id or active.id) if active else None,
            "cat_qs": f"&category={active.slug}" if active else "",
        },
    )


@login_required
def post_detail(request, pk):
    post = get_object_or_404(Post, pk=pk)
    if request.method == "POST":
        form = CommentForm(request.POST)
        if form.is_valid():
            c = form.save(commit=False)
            c.post = post
            c.author = request.user
            c.save()
            notify(post.author, request.user, Notification.COMMENT, post)
            return redirect("post_detail", pk=pk)
    else:
        form = CommentForm()
    annotated = _annotate(Post.objects.filter(pk=pk), request.user)[0]
    comments = post.comments.select_related("author", "author__profile")
    return render(request, "social/post_detail.html", {"post": annotated, "comments": comments, "form": form})


@login_required
@require_POST
def delete_post(request, pk):
    post = get_object_or_404(Post, pk=pk, author=request.user)
    post.delete()
    messages.success(request, "Post deleted.")
    return redirect("feed")


@login_required
@require_POST
def delete_comment(request, pk):
    comment = get_object_or_404(Comment, pk=pk, author=request.user)
    post_id = comment.post_id
    comment.delete()
    return redirect("post_detail", pk=post_id)


@login_required
@require_POST
def toggle_like(request, pk):
    post = get_object_or_404(Post, pk=pk)
    like, created = Like.objects.get_or_create(user=request.user, post=post)
    if created:
        notify(post.author, request.user, Notification.LIKE, post)
    else:
        like.delete()
        Notification.objects.filter(
            recipient=post.author, actor=request.user, kind=Notification.LIKE, post=post
        ).delete()
    return JsonResponse({"liked": created, "count": post.likes.count()})


@login_required
@require_POST
def toggle_follow(request, username):
    target = get_object_or_404(User, username=username)
    if target == request.user:
        return JsonResponse({"error": "You cannot follow yourself."}, status=400)
    rel, created = Follow.objects.get_or_create(follower=request.user, following=target)
    if created:
        notify(target, request.user, Notification.FOLLOW)
    else:
        rel.delete()
        Notification.objects.filter(
            recipient=target, actor=request.user, kind=Notification.FOLLOW
        ).delete()
    return JsonResponse({"following": created, "followers": target.followers.count()})


@login_required
def profile(request, username):
    owner = get_object_or_404(User.objects.select_related("profile"), username=username)
    posts = _annotate(owner.posts.all(), request.user)
    is_following = Follow.objects.filter(follower=request.user, following=owner).exists()
    return render(
        request,
        "social/profile.html",
        {
            "owner": owner,
            "posts": posts,
            "is_following": is_following,
            "follower_count": owner.followers.count(),
            "following_count": owner.following.count(),
        },
    )


@login_required
def follow_list(request, username, kind):
    owner = get_object_or_404(User, username=username)
    if kind == "followers":
        users = User.objects.filter(following__following=owner)
    else:
        users = User.objects.filter(followers__follower=owner)
    return render(
        request,
        "social/follow_list.html",
        {"owner": owner, "users": users.select_related("profile"), "kind": kind},
    )


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST or None, request.FILES or None, instance=request.user.profile)
    if request.method == "POST" and form.is_valid():
        form.save()
        return redirect("profile", username=request.user.username)
    return render(request, "social/edit_profile.html", {"form": form})


@login_required
def search(request):
    q = request.GET.get("q", "").strip()
    users = User.objects.filter(username__icontains=q).select_related("profile")[:20] if q else []
    return render(request, "social/search.html", {"q": q, "users": users})


@login_required
@require_POST
def toggle_bookmark(request, pk):
    post = get_object_or_404(Post, pk=pk)
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)
    if not created:
        bookmark.delete()
    return JsonResponse({"saved": created})


@login_required
def saved(request):
    ids = list(
        Bookmark.objects.filter(user=request.user).order_by("-created_at").values_list("post_id", flat=True)
    )
    return render(request, "social/saved.html", {"posts": _posts_in_order(ids, request.user)})


@login_required
def notifications(request):
    items = list(
        request.user.notifications.select_related("actor", "actor__profile", "post")[:50]
    )
    for n in items:
        n.is_new = not n.is_read
    request.user.notifications.filter(is_read=False).update(is_read=True)
    return render(request, "social/notifications.html", {"items": items, "unread_notifications": 0})


@login_required
def inbox(request):
    me = request.user
    unread = dict(
        me.received_messages.filter(is_read=False).values_list("sender").annotate(n=Count("id"))
    )
    conversations, seen = [], set()
    recent = (
        Message.objects.filter(Q(sender=me) | Q(recipient=me))
        .select_related("sender", "sender__profile", "recipient", "recipient__profile")
        .order_by("-created_at")
    )
    for m in recent:
        partner = m.recipient if m.sender_id == me.id else m.sender
        if partner.id in seen:
            continue
        seen.add(partner.id)
        conversations.append(
            {"partner": partner, "last": m, "mine": m.sender_id == me.id, "unread": unread.get(partner.id, 0)}
        )
    people = (
        User.objects.filter(followers__follower=me).exclude(id__in=seen).select_related("profile")[:8]
    )
    return render(request, "social/inbox.html", {"conversations": conversations, "people": people})


@login_required
def thread(request, username):
    partner = get_object_or_404(User.objects.select_related("profile"), username=username)
    if partner == request.user:
        return redirect("inbox")
    if request.method == "POST":
        body = request.POST.get("body", "").strip()[:1000]
        if body:
            Message.objects.create(sender=request.user, recipient=partner, body=body)
        return redirect("thread", username=username)
    chat = Message.objects.filter(
        Q(sender=request.user, recipient=partner) | Q(sender=partner, recipient=request.user)
    ).order_by("created_at")
    chat = list(chat)
    Message.objects.filter(sender=partner, recipient=request.user, is_read=False).update(is_read=True)
    return render(
        request, "social/thread.html", {"partner": partner, "chat": chat, "unread_messages": 0}
    )


@login_required
def activity(request):
    me = request.user
    liked_ids = list(
        Like.objects.filter(user=me).order_by("-created_at").values_list("post_id", flat=True)[:20]
    )
    comments = me.comments.select_related("post", "post__author").order_by("-created_at")[:20]
    return render(
        request,
        "social/activity.html",
        {
            "liked_posts": _posts_in_order(liked_ids, me),
            "comments": comments,
            "counts": {
                "posts": me.posts.count(),
                "likes": me.likes.count(),
                "comments": me.comments.count(),
                "saved": me.bookmarks.count(),
            },
        },
    )


class PasswordChange(SuccessMessageMixin, auth_views.PasswordChangeView):
    template_name = "social/password_change.html"
    success_url = reverse_lazy("edit_profile")
    success_message = "Password updated."
