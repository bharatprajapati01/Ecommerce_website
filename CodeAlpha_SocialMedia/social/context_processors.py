def badges(request):
    """Unread counts shown as red badges on the Messages and Notifications nav items."""
    user = getattr(request, "user", None)
    if user is None or not user.is_authenticated:
        return {}
    return {
        "unread_notifications": user.notifications.filter(is_read=False).count(),
        "unread_messages": user.received_messages.filter(is_read=False).count(),
    }
