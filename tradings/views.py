from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from contacts.models import Chat
from .models import TradingRecord
from django.contrib.auth.decorators import login_required



@login_required
def submit_review(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id)
    if request.user not in [chat.buyer, chat.seller]:
        return redirect("accounts:dashboard")

    record, created = TradingRecord.objects.get_or_create(chat=chat)

    if request.method == "POST":
        comment = request.POST.get("comment_content", "").strip()
        star = request.POST.get("star")

        # 防止重複評價
        if request.user == chat.buyer and record.buyer_star is not None:
            messages.error(request, "你已經評價過這次交易了")
            return redirect("contacts:chat_detail", chat.id)
        if request.user == chat.seller and record.seller_star is not None:
            messages.error(request, "你已經評價過這次交易了")
            return redirect("contacts:chat_detail", chat.id)

        if not comment:
            messages.error(request, "請填寫評論內容")
            return redirect("contacts:chat_detail", chat.id)

        try:
            star = int(star)
            if not (1 <= star <= 5):
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, "請選擇 1-5 星評分")
            return redirect("contacts:chat_detail", chat.id)

        if request.user == chat.buyer:
            record.buyer_comment = comment
            record.buyer_star = star
        else:
            record.seller_comment = comment
            record.seller_star = star

        # 雙方都評價完，才標記交易完成 + 公開
        if record.buyer_star is not None and record.seller_star is not None:
            record.is_public = True
            chat.trade_finished = True
            chat.save()

        record.save()
        messages.success(request, "評價已送出")
        return redirect("accounts:dashboard")

    return render(request, "tradings/submit_review.html", {"chat": chat, "record": record})


def public_record(request, record_id):
    record = get_object_or_404(TradingRecord, id=record_id, is_public=True)
    return render(request, "tradings/public_record.html", {"record": record})
