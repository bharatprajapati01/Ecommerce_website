from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

urlpatterns = [
    path("", views.for_you, name="for_you"),
    path("products/", views.product_list, name="product_list"),
    path("category/<slug:category_slug>/", views.product_list, name="category"),
    path("product/<slug:slug>/", views.product_detail, name="product_detail"),
    path("cart/", views.cart_detail, name="cart_detail"),
    path("cart/add/<int:product_id>/", views.cart_add, name="cart_add"),
    path("cart/remove/<int:product_id>/", views.cart_remove, name="cart_remove"),
    path("checkout/", views.checkout, name="checkout"),
    path("orders/", views.order_history, name="order_history"),
    path("orders/<int:order_id>/success/", views.order_success, name="order_success"),
    path("info/<slug:slug>/", views.info_page, name="info_page"),
    path("account/", views.account_profile, name="account_profile"),
    path("account/addresses/", views.account_addresses, name="account_addresses"),
    path("account/addresses/<int:address_id>/delete/", views.address_delete, name="address_delete"),
    path("account/addresses/<int:address_id>/default/", views.address_make_default, name="address_make_default"),
    path("account/wishlist/", views.account_wishlist, name="account_wishlist"),
    path("account/wishlist/toggle/<int:product_id>/", views.wishlist_toggle, name="wishlist_toggle"),
    path("account/notifications/", views.account_notifications, name="account_notifications"),
    path("account/coupons/", views.account_coupons, name="account_coupons"),
    path("accounts/register/", views.register, name="register"),
    path(
        "accounts/login/",
        auth_views.LoginView.as_view(template_name="registration/login.html"),
        name="login",
    ),
    path("accounts/logout/", auth_views.LogoutView.as_view(), name="logout"),
]
