#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
注入壞資料 (Bad Data) — 模擬 bug，供救災程序演練
================================================

這支程式會故意把「壞資料」寫進資料庫，製造各種 bug：

  * 重複的店鋪（相同地址）
  * 空店名、空地址
  * 亂填的電話 / 網站
  * 非法的卡牌分類 / 屬性 / 階段 / 稀有度
  * 負數 HP、誇張的經緯度

之後可用 data_manager.py（Drop → 建立 Table → Import）還原到乾淨狀態。

用法：
  python insert_bad_data.py
"""

import os
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from shops.models import Shoplist  # noqa: E402
from cards.models import Card, Generation  # noqa: E402


def main() -> None:
    print("開始注入壞資料…\n")

    # 1) 重複店鋪（跟現有 Top Draw 相同地址 → 製造重複資料）
    dup_address = "觀塘開源道72號溢財中心地下A2舖"
    for i in range(3):
        Shoplist.objects.create(
            shopname=f"重複壞店{i}", address=dup_address, district="Kwun Tong",
            phone_number="00000000", website="bad-shop.com",
        )
    print("  [1] 重複店鋪 ×3（相同地址）")

    # 2) 空店名 + 空地址
    Shoplist.objects.create(shopname="", address="", district="Unknown")
    print("  [2] 空店名、空地址 ×1")

    # 3) 亂填電話 / 網站 / 誇張經緯度
    Shoplist.objects.create(
        shopname="亂填資料店", address="亂填地址123", district="Unknown",
        phone_number="not-a-phone", website="this is not a url",
        latitude=999.0, longitude=-999.0,
    )
    print("  [3] 亂填電話/網站 + 誇張經緯度 ×1")

    # 4) 壞的世代（空名稱、0 張卡）
    bad_gen = Generation.objects.create(name="", total_cards=0)
    print("  [4] 壞世代（空名稱、total_cards=0）×1")

    # 5) 壞卡牌（非法分類/屬性/階段/稀有度、空 title、負數 HP）
    Card.objects.create(
        title="", category="WrongCategory", energy_type="WrongType",
        stage="WrongStage", rarity="WrongRarity", hp=-999,
        card_number=99999, generation=bad_gen, photo_main="", transaction=0,
    )
    Card.objects.create(
        title="負血卡", category="Pokemon", energy_type="Fire",
        stage="Basic", rarity="C", hp=-1,
        card_number=1, generation=bad_gen, photo_main="", transaction=0,
    )
    print("  [5] 壞卡牌（非法欄位 + 負數 HP）×2")

    print("\n壞資料注入完成。")
    print(f"  Shoplist  : {Shoplist.objects.count()} 筆")
    print(f"  Card      : {Card.objects.count()} 筆")
    print(f"  Generation: {Generation.objects.count()} 筆")


if __name__ == "__main__":
    main()
