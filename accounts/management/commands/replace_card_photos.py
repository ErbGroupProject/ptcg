import os
import shutil
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from cards.models import Card

IMAGE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


class Command(BaseCommand):
    help = "用自己的卡照批次替換 Card.photo_main（依檔名對應 title 或 card_number）"

    def add_arguments(self, parser):
        parser.add_argument(
            "--source",
            type=str,
            default="replace_photos",
            help="放自己卡照的資料夾（相對路徑會從專案根目錄找）",
        )
        parser.add_argument(
            "--match",
            type=str,
            choices=["title", "number"],
            default="title",
            help="用卡片 title（如 tw19551）或 card_number（如 1 / 001）對應檔名",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="只預覽對應結果，不實際寫入",
        )

    def handle(self, *args, **options):
        source = options["source"]
        if not os.path.isabs(source):
            source = os.path.join(settings.BASE_DIR, source)
        if not os.path.isdir(source):
            raise CommandError(f"找不到資料夾：{source}")

        match = options["match"]
        dry_run = options["dry_run"]

        files = [
            f for f in os.listdir(source)
            if Path(f).suffix.lower() in IMAGE_EXTS
        ]

        # 建立「檔名(不含副檔名) -> Card」對照表
        lookup = {}
        dup_keys = set()

        for card in Card.objects.all():
            key = card.title if match == "title" else str(card.card_number)
            if key in lookup:
                # card_number 會有重複（tw 卡 1~79 與 Gen Card 1~30 重疊）
                dup_keys.add(key)
                continue
            lookup[key] = card

        # 重複的 key 直接移除，避免誤換到錯的卡
        for key in dup_keys:
            lookup.pop(key, None)

        # 用 card_number 時，額外支援 001 這種零補齊格式
        # （只針對「無重複」的編號，避免 001~030 又被誤加回來）
        if match == "number":
            for card in Card.objects.all():
                if str(card.card_number) in dup_keys:
                    continue
                lookup.setdefault(f"{card.card_number:03d}", card)

        replaced = 0
        skipped = 0
        unmatched = []

        for fname in sorted(files):
            stem = Path(fname).stem  # 去掉副檔名
            card = lookup.get(stem)

            if card is None:
                if stem in dup_keys:
                    self.stdout.write(self.style.WARNING(
                        f"⚠️  略過 {fname}：檔名 {stem} 對應到多張卡，無法判定"
                    ))
                else:
                    unmatched.append(fname)
                skipped += 1
                continue

            ext = Path(fname).suffix.lower()
            today = timezone.now().strftime("%Y/%m/%d")
            dest_name = f"card_{card.id}{ext}"
            rel_path = f"photos/{today}/{dest_name}"
            dest = os.path.join(settings.MEDIA_ROOT, *rel_path.split("/"))

            if dry_run:
                self.stdout.write(
                    f"[dry-run] {fname} -> {rel_path}（card #{card.id} {card.title}）"
                )
            else:
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                shutil.copy2(os.path.join(source, fname), dest)
                card.photo_main = rel_path
                card.save(update_fields=["photo_main"])
                self.stdout.write(
                    f"✅ {fname} -> card #{card.id} {card.title}"
                )

            replaced += 1

        summary = f"完成：替換 {replaced} 張，略過 {skipped} 張"
        if unmatched:
            summary += f"，未對應 {len(unmatched)} 張：{', '.join(unmatched)}"
        self.stdout.write(self.style.SUCCESS(summary))
