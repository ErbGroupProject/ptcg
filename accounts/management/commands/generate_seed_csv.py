from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = '建立 20 個測試使用者 (user1~user20，密碼 1234)'

    def handle(self, *args, **options):
        created = 0
        for i in range(1, 21):
            username = f'user{i}'
            user, is_new = User.objects.get_or_create(username=username)
            user.email = '1234@1234.com'
            user.first_name = ''
            user.last_name = ''
            user.is_staff = False
            user.is_superuser = False
            user.is_active = True
            user.set_password('1234')
            user.save()
            if is_new:
                created += 1

        self.stdout.write(self.style.SUCCESS(f'完成：新增 {created} 個使用者'))
