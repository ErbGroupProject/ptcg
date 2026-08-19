from django.db.models import Q
from contacts.models import Message


def unread_count(request):
    if request.user.is_authenticated:
        count = Message.objects.filter(
            Q(chat__buyer=request.user) | Q(chat__seller=request.user)
        ).exclude(sender=request.user).filter(is_read=False).count()
    else:
        count = 0
    return {"unread_count": count}
