from django.db import models
from contacts.models import Chat


class TradingRecord(models.Model):
    chat = models.OneToOneField(Chat, on_delete=models.CASCADE, related_name="trading_record")
    buyer_comment = models.TextField(blank=True)
    buyer_star = models.IntegerField(blank=True, null=True)
    seller_comment = models.TextField(blank=True)
    seller_star = models.IntegerField(blank=True, null=True)
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"TradingRecord-{self.chat.id}"
