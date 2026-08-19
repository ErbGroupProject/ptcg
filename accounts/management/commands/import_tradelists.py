import os
import shutil
from django.conf import settings
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import Profile
from listings.models import Tradelist


class Command(BaseCommand):
    help = '將 static/image 的 tw 卡片圖建立成 Tradelist 貼文'

    def handle(self, *args, **kwargs):
        # 1. 確保 20 個 Profile 存在
        profiles = []
        for n in range(1, 21):
            username = f"user{n}"
            user = User.objects.get(username=username)
            profile, _ = Profile.objects.get_or_create(user=user)
            profiles.append(profile)

        # 2. 來源與目標目錄
        src_dir = os.path.join(settings.BASE_DIR, 'static', 'image')
        media_dir = os.path.join(settings.MEDIA_ROOT, 'photos', '2026', '08', '18')
        os.makedirs(media_dir, exist_ok=True)

        # 3. 建立貼文
        created = 0
        for i in range(19551, 19630):
            fname = f"tw{i:08d}.png"          # tw00019551.png（8 位補零）
            src = os.path.join(src_dir, fname)
            if not os.path.exists(src):
                self.stdout.write(self.style.WARNING(f"缺少 {fname}，跳過"))
                continue

            # 複製到 media
            dst = os.path.join(media_dir, fname)
            shutil.copy2(src, dst)

            # 輪流分配給 20 人
            profile = profiles[(i - 19551) % len(profiles)]

            Tradelist.objects.create(
                user_name=profile,
                sell_item_name=fname,                          # 卡名先用檔名佔位
                sell_item_main_photo=f"photos/2026/08/18/{fname}",  # media 相對路徑
                price=100,
                condition="未使用",
            )
            created += 1

        self.stdout.write(self.style.SUCCESS(f"完成，共建立 {created} 筆 Tradelist"))
