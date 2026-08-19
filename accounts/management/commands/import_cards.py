import os
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand
from cards.models import Card, Generation


class Command(BaseCommand):
    help = "Import card images from static/image into the Card model"

    START_NUMBER = 19551
    END_NUMBER = 19630  # exclusive: 19551 ~ 19629
    GENERATION_NAME = "Test Generation"

    def handle(self, *args, **options):
        total_cards = self.END_NUMBER - self.START_NUMBER

        generation, _ = Generation.objects.get_or_create(
            name=self.GENERATION_NAME,
            defaults={"total_cards": total_cards},
        )

        if generation.total_cards != total_cards:
            generation.total_cards = total_cards
            generation.save(update_fields=["total_cards"])

        src_dir = os.path.join(settings.BASE_DIR, "static", "image")
        media_dir = os.path.join(
            settings.MEDIA_ROOT, "photos", "2026", "08", "18"
        )
        os.makedirs(media_dir, exist_ok=True)

        created_count = 0
        skipped_count = 0
        missing_count = 0

        for index, number in enumerate(
            range(self.START_NUMBER, self.END_NUMBER), start=1
        ):
            filename = f"tw{number:08d}.png"
            src = os.path.join(src_dir, filename)

            if not os.path.exists(src):
                self.stdout.write(
                    self.style.WARNING(f"Missing image: {filename} - skipped")
                )
                missing_count += 1
                continue

            title = f"tw{number}"
            card_number = index

            if Card.objects.filter(
                generation=generation,
                card_number=card_number,
            ).exists():
                skipped_count += 1
                continue

            destination = os.path.join(media_dir, filename)
            if not os.path.exists(destination):
                shutil.copy2(src, destination)

            Card.objects.create(
                category="Pokemon",
                photo_main=f"photos/2026/08/18/{filename}",
                stage="Basic",
                rarity="C",
                title=title,
                hp=100,
                energy_type="Colorless",
                card_number=card_number,
                generation=generation,
                transaction=0,
            )

            created_count += 1
            self.stdout.write(
                f"Created {card_number:03d}/{total_cards:03d}: {title}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count} Cards, "
                f"skipped {skipped_count}, missing {missing_count}."
            )
        )
