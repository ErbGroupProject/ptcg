import json
from django.core.management.base import BaseCommand
from accounts.models import Profile
from django.utils import timezone



class Command(BaseCommand):
    help = "為 user1~user20 產生 Tradelist fixture JSON（卡片輪流分配）"

    PHOTO_DIR = "photos/2026/08/18"   # 圖片實際放進 media 後的相對路徑

    def build_cards(self):
        cards = []
        for n in range(19551, 19630):        # tw00019551 ~ tw00019629，共 79 張
            filename = f"tw{n}.png"
            # TODO: 把真正卡名填進來；暫時先用檔名佔位
            card_name = filename.replace(".png", "")
            cards.append({
                "name": card_name,
                "photo": filename,
                "series_name": "",        # TODO: 填系列名
                "series_number": "",      # TODO: 填系列編號
            })
        return cards

    def handle(self, *args, **kwargs):
        # ⚠️ 外鍵是 Profile，不是 User；這裡假設 Profile 有 user 欄位指向 User
        profiles = list(
            Profile.objects.filter(user__username__startswith="user")
            .order_by("user__username")
        )
        if len(profiles) < 20:
            self.stderr.write(
                f"⚠️ 只找到 {len(profiles)} 個 Profile，"
                "請先建立 user1~user20 並確認每個都有對應 Profile。"
            )
            if not profiles:
                return

        cards = self.build_cards()
        fixtures = []

        for i, card in enumerate(cards):
            profile = profiles[i % len(profiles)]   # 輪流 user1 → user20
            fixtures.append({
                "model": "listings.tradelist",
                "pk": None,
                "fields": {
                    "user_name": profile.pk,
                    "sell_item_name": card["name"],
                    "sell_item_main_photo": f"{self.PHOTO_DIR}/{card['photo']}",
                    "photo_2": "",
                    "photo_3": "",
                    "photo_4": "",
                    "photo_5": "",
                    "photo_6": "",
                    "photo_7": "",
                    "photo_8": "",
                    "photo_9": "",
                    "price": 100,                 # TODO: 改成你要的價格
                    "condition": "NM",            # TODO: 改成你要的品質
                    "identification_score": None,
                    "series_name": card["series_name"],
                    "series_number": card["series_number"],
                    "descriptions": "",
                    "deal_place": "",
                    "is_sold": False,
                    "list_date": timezone.now().isoformat(), 
                },
            })
            

        path = "seed_tradelists.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fixtures, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"✅ 產生 {len(fixtures)} 筆到 {path}"))
        profiles = list(Profile.objects.filter(user__username__startswith="user"))
        if not profiles:
            raise SystemExit('找不到任何 Profile，請先執行 python manage.py ensure_profiles')
        
