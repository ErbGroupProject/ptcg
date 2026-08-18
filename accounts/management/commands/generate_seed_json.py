import json

from django.contrib.auth.hashers import make_password
from django.core.management.base import BaseCommand
from django.utils import timezone


class Command(BaseCommand):
    help = "產生 seed_users.json（Django fixture，內含 user1~user20）"

    def handle(self, *args, **options):
        now = timezone.now().isoformat()
        fixtures = []

        for i in range(1, 21):
            fixtures.append({
                "model": "auth.user",
                "pk": None,  # 不指定 id，讓 DB 自動編號，避免衝突
                "fields": {
                    "password": make_password("1234"),  # 每個帳號獨立 salt 的真雜湊
                    "is_superuser": False,
                    "username": f"user{i}",
                    "first_name": "User",
                    "last_name": str(i),
                    "email": "1234@1234.com",
                    "is_staff": False,
                    "is_active": True,
                    "date_joined": now,
                },
            })

        path = "seed_users.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(fixtures, f, ensure_ascii=False, indent=2)

        self.stdout.write(self.style.SUCCESS(f"✅ 已產生 {path}（20 筆：user1~user20）"))
