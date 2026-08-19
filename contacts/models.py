from django.db import models
from django.contrib.auth.models import User
from listings.models import Tradelist   # ← 改成 Tradelist


class Chat(models.Model):
    listing = models.ForeignKey(Tradelist, on_delete=models.CASCADE, related_name="chat_room")
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="buyer_chats")
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name="seller_chats")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    trade_finished = models.BooleanField(default=False, verbose_name="交易是否標記完成")

    class Meta:
        unique_together = ["listing", "buyer", "seller"]
    @property
    def review_record(self):
        from tradings.models import TradingRecord
        return TradingRecord.objects.filter(chat=self).first()

    def __str__(self):
        return f"Chat-{self.listing.sell_item_name} | {self.buyer.username}-{self.seller.username}"   # ← topic 改 sell_item_name


class Message(models.Model):
    chat = models.ForeignKey(Chat, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"{self.sender.username}: {self.content[:30]}"
