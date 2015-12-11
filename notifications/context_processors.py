from notifications.models import Notification
from user.models import UserProfile


def notification_context(request):
    if request.user.is_authenticated():
        profile = UserProfile.get_or_create_profile(request.user)
        notifications = list(Notification.get_notification(profile))
        unread = sum(not notification.is_read for notification in notifications)
        return {'notifications': notifications, 'unread': unread}

    return {'notifications': [], 'unread': 0}
