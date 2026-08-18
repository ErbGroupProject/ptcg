from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile


class Command(BaseCommand):
    help = '為 user1~user20 建立缺少的 Profile（冪等，可重複執行）'

    def handle(self, *args, **options):
        created = 0
        missing_users = []

        for i in range(1, 21):
            username = f'user{i}'
            user = User.objects.filter(username=username).first()
            if not user:
                missing_users.append(username)
                self.stdout.write(self.style.WARNING(f'找不到使用者 {username}，跳過'))
                continue

            _, was_created = Profile.objects.get_or_create(user=user)
            if was_created:
                created += 1
                self.stdout.write(f'建立 Profile: {username}')

        self.stdout.write(self.style.SUCCESS(f'完成，共新增 {created} 個 Profile'))
        if missing_users:
            self.stdout.write(self.style.WARNING(f'以下帳號不存在，請先確認帳號已建立：{missing_users}'))
