import json
import os
from io import StringIO

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

# 要備份的 app：
#   auth.User = 使用者帳號（Profile / Chat / Tradelist 都依賴它）
#   （不導出 auth.Permission / auth.Group / contenttypes，
#    這些是 Django post_migrate 自動管理的資料，導入時會自動重建）
APPS = [
    "auth.User",
    "pages",
    "accounts",
    "shops",
    "listings",
    "tradings",
    "contacts",
    "cards",
    "banners",
]


class Command(BaseCommand):
    help = "導出所有資料到 JSON（災難恢復備份）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--output",
            type=str,
            default="export_all.json",
            help="輸出檔名（預設 export_all.json；相對路徑會放到專案根目錄）",
        )

    def handle(self, *args, **options):
        output = options["output"]

        # 相對路徑一律基於專案根目錄（BASE_DIR），避免因執行目錄不同而找不到檔
        if not os.path.isabs(output):
            output = os.path.join(settings.BASE_DIR, output)

        buf = StringIO()
        call_command(
            "dumpdata",
            *APPS,
            natural_foreign=True,
            natural_primary=True,
            indent=2,
            stdout=buf,
        )

        data = buf.getvalue()
        os.makedirs(os.path.dirname(output), exist_ok=True)
        with open(output, "w", encoding="utf-8") as f:
            f.write(data)

        count = len(json.loads(data))
        self.stdout.write(self.style.SUCCESS(f"✅ 已導出 {count} 筆資料 → {output}"))
