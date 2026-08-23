from django.core.management import call_command
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "已格式化"

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING("⚠️  即將清空資料庫所有資料..."))
        call_command("flush", interactive=False)
        self.stdout.write(self.style.SUCCESS("✅ 已格式化"))
