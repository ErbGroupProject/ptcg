from django.db.models import Q
from .models import Message


def unread_messages(request):
    if not request.user.is_authenticated:
        return {'unread_count': 0}
    count = Message.objects.filter(
        Q(chat__buyer=request.user) | Q(chat__seller=request.user),
        is_read=False,
    ).exclude(sender=request.user).count()
    return {'unread_count': count}
