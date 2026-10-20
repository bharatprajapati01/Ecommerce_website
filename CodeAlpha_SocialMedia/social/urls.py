from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.feed, name="feed"),
    path("signup/", views.signup, name="signup"),
    path("login/", auth_views.LoginView.as_view(template_name="social/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("search/", views.search, name="search"),
    path("settings/profile/", views.edit_profile, name="edit_profile"),
    path("settings/password/", views.PasswordChange.as_view(), name="password_change"),
    path("saved/", views.saved, name="saved"),
    path("notifications/", views.notifications, name="notifications"),
    path("messages/", views.inbox, name="inbox"),
    path("messages/<str:username>/", views.thread, name="thread"),
    path("activity/", views.activity, name="activity"),
    path("post/<int:pk>/", views.post_detail, name="post_detail"),
    path("post/<int:pk>/delete/", views.delete_post, name="delete_post"),
    path("post/<int:pk>/like/", views.toggle_like, name="toggle_like"),
    path("post/<int:pk>/save/", views.toggle_bookmark, name="toggle_bookmark"),
    path("comment/<int:pk>/delete/", views.delete_comment, name="delete_comment"),
    path("u/<str:username>/", views.profile, name="profile"),
    path("u/<str:username>/follow/", views.toggle_follow, name="toggle_follow"),
    path("u/<str:username>/<str:kind>/", views.follow_list, name="follow_list"),
]
