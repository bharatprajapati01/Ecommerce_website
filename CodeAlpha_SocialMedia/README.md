# Circle – Mini Social Media Platform

CodeAlpha Full Stack Development Internship – **Task 2**.

A small social network built with **Django** (backend) and **HTML, CSS, JavaScript** (frontend).

## Features

- **User profiles** – sign up / log in, bio, avatar upload, post/follower/following counts
- **Posts & comments** – create text/image posts, comment on any post, delete your own
- **Like system** – like/unlike posts instantly (AJAX, no page reload)
- **Follow system** – follow/unfollow users, followers/following lists
- **Feed** – "Following" feed (people you follow + you) or "Everyone"
- **Search** – find people by username
- Suggested people to follow, pagination, CSRF protection, login-required pages

## Database (SQLite via Django ORM)

| Model | Purpose |
|---|---|
| `User` (Django built-in) | accounts |
| `Profile` | bio + avatar, one per user (auto-created) |
| `Post` | author, content, optional image |
| `Comment` | post, author, content |
| `Like` | user + post (unique pair) |
| `Follow` | follower + following (unique pair, no self-follow) |

## Run it

```bash
pip install django pillow
python manage.py migrate
python manage.py createsuperuser   # optional, for /admin
python manage.py runserver
```

Open http://127.0.0.1:8000/ , sign up two accounts, follow each other, and post.

## Tests

```bash
python manage.py test
```

## Structure

```
config/            Django project settings and root URLs
social/models.py   database models
social/views.py    pages + JSON endpoints for like/follow
social/templates/  HTML templates
social/static/     style.css, app.js
```

## Submission note

Push to a GitHub repo named `CodeAlpha_SocialMedia` (format `CodeAlpha_ProjectName`).
