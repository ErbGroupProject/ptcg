import os
import random
import shutil

from django.conf import settings
from django.core.management.base import BaseCommand

from cards.models import Card, Generation
from cards.choices import (
    category_choices,
    energy_choices,
    stage_choices,
    rarity_choices,
    generation_choices,
)


class Command(BaseCommand):
    help = "Import card images and create randomized test Card data"

    START_NUMBER = 19551
    END_NUMBER = 19630  # 19551 ~ 19629, 79 cards

    def handle(self, *args, **options):
        total_cards = self.END_NUMBER - self.START_NUMBER

        src_dir = os.path.join(
            settings.BASE_DIR,
            "static",
            "image",
        )

        media_dir = os.path.join(
            settings.MEDIA_ROOT,
            "photos",
            "2026",
            "08",
            "18",
        )
        os.makedirs(media_dir, exist_ok=True)

        categories = list(category_choices.keys())
        energy_types = list(energy_choices.keys())
        stages = list(stage_choices.keys())
        rarities = list(rarity_choices.keys())
        generation_names = list(generation_choices.keys())

        created_count = 0
        skipped_count = 0
        missing_count = 0

        for index, number in enumerate(
            range(self.START_NUMBER, self.END_NUMBER),
            start=1,
        ):
            filename = f"tw{number:08d}.png"
            src = os.path.join(src_dir, filename)

            if not os.path.exists(src):
                self.stdout.write(
                    self.style.WARNING(
                        f"Missing image: {filename} - skipped"
                    )
                )
                missing_count += 1
                continue

            title = f"tw{number}"
            card_number = index

            if Card.objects.filter(
                title=title,
                card_number=card_number,
            ).exists():
                skipped_count += 1
                continue

            category = random.choice(categories)
            energy_type = random.choice(energy_types)
            stage = random.choice(stages)
            rarity = random.choice(rarities)
            generation_name = random.choice(generation_names)

            generation, _ = Generation.objects.get_or_create(
                name=generation_name,
                defaults={"total_cards": total_cards},
            )

            if generation.total_cards != total_cards:
                generation.total_cards = total_cards
                generation.save(update_fields=["total_cards"])

            destination = os.path.join(media_dir, filename)

            if not os.path.exists(destination):
                shutil.copy2(src, destination)

            Card.objects.create(
                category=category,
                photo_main=f"photos/2026/08/18/{filename}",
                stage=stage,
                rarity=rarity,
                title=title,
                hp=random.randint(1, 250),
                energy_type=energy_type,
                card_number=card_number,
                generation=generation,
                transaction=random.choice([0, 0, 0, 1]),
            )

            created_count += 1

            self.stdout.write(
                f"Created {card_number:03d}/{total_cards:03d}: "
                f"{title} | {category} | {stage} | {rarity} | "
                f"HP {Card.objects.get(title=title, card_number=card_number).hp} | "
                f"{energy_type} | {generation_name}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Done. Created {created_count} Cards, "
                f"skipped {skipped_count}, "
                f"missing {missing_count}."
            )
        )
