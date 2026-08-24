from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.db import connection


class Command(BaseCommand):
    help = "清空資料庫並 DROP 所有 Table（災難恢復：先 export_data 備份，再執行本命令，最後 import_data）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--noinput",
            action="store_true",
            help="不詢問確認，直接執行（適合寫進腳本）",
        )
        parser.add_argument(
            "--no-migrate",
            action="store_true",
            help="只 drop table，不重新 migrate（之後要自己跑 migrate）",
        )

    def handle(self, *args, **options):
        engine = settings.DATABASES["default"]["ENGINE"]

        # 破壞性操作，先確認
        if not options["noinput"]:
            self.stdout.write(
                self.style.WARNING("⚠️  這會 DROP 資料庫所有 Table 並清空所有資料！")
            )
            answer = input("確定嗎？輸入 yes 繼續：").strip().lower()
            if answer != "yes":
                self.stdout.write(self.style.WARNING("已取消"))
                return

        if "postgresql" in engine:
            self._drop_postgres()
        else:
            # 其他資料庫：退而求其次用 flush（truncate，只清資料、不 drop table）
            self.stdout.write(self.style.WARNING("非 PostgreSQL：改用 flush（truncate）"))
            call_command("flush", interactive=False)

        if not options["no_migrate"]:
            self.stdout.write("重新建立所有 Table（migrate）...")
            call_command("migrate", interactive=False)

        self.stdout.write(self.style.SUCCESS("✅ 已清空並重新建立所有 Table"))

    def _drop_postgres(self):
        # DROP SCHEMA public CASCADE：一口氣刪掉所有 table、sequence、view
        # CREATE SCHEMA public：重建空的 schema，之後 migrate 會重新建 table
        with connection.cursor() as cursor:
            cursor.execute("DROP SCHEMA public CASCADE")
            cursor.execute("CREATE SCHEMA public")
        self.stdout.write("已執行 DROP SCHEMA public CASCADE + CREATE SCHEMA public")
