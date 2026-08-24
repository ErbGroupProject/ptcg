import json
import os
import tempfile

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand

# 這些 model 由 Django 自動管理（post_migrate 重建），不該手動導入，
# 匯入時自動跳過，避免「Permission has no content_type」這類錯誤。
SKIP_MODELS = {"auth.permission", "auth.group", "contenttypes.contenttype"}


class Command(BaseCommand):
    help = "從 JSON 匯入資料（災難恢復，含 User 與密碼 hash）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--input",
            type=str,
            default="export_all.json",
            help="要匯入的 JSON 檔（預設 export_all.json；相對路徑會從專案根目錄找）",
        )
        parser.add_argument(
            "--no-migrate",
            action="store_true",
            help="跳過 migrate，直接 loaddata（適用於 Table 已存在的狀況）",
        )

    def handle(self, *args, **options):
        input_file = options["input"]

        if not os.path.isabs(input_file):
            input_file = os.path.join(settings.BASE_DIR, input_file)

        if not os.path.exists(input_file):
            self.stdout.write(self.style.ERROR(f"找不到檔案：{input_file}"))
            return

        # 若剛 drop 過 table，先 migrate 重建所有 table（已存在時 migrate 是 no-op）
        if not options["no_migrate"]:
            self.stdout.write("確保 Table 存在（migrate）...")
            call_command("migrate", interactive=False)

        # 讀取並過濾掉系統自動管理的 model
        with open(input_file, encoding="utf-8") as f:
            data = json.load(f)

        filtered = [o for o in data if o.get("model") not in SKIP_MODELS]
        skipped = len(data) - len(filtered)
        if skipped:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  已跳過 {skipped} 筆系統自動管理的資料"
                    f"（auth.permission / auth.group / contenttypes）"
                )
            )

        # 寫到暫存檔再匯入
        with tempfile.NamedTemporaryFile(
            "w", suffix=".json", delete=False, encoding="utf-8"
        ) as tmp:
            json.dump(filtered, tmp, ensure_ascii=False, indent=2)
            tmp_path = tmp.name

        try:
            call_command("loaddata", tmp_path, verbosity=1)
            self.stdout.write(
                self.style.SUCCESS(
                    f"✅ 已從 {input_file} 匯入完成（User 帳號與密碼 hash 已還原，可用原密碼登入）"
                )
            )
        finally:
            os.unlink(tmp_path)
