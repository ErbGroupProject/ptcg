#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
PTCG 資料管理員 (Data Manager) — 單一程式整合五大功能
====================================================

把「導出 / 清理 / 刪除+Drop / 建立 Table / 匯入」整合在同一個程式裡，
執行時用互動選單選擇要跑的功能，並支援多選（例如輸入 1,3,5）。

五大功能：
  1) Export Data      導出資料庫 → data_export.json（備份）
  2) Clean Data       清理原始資料 ptcg shops data.txt → 匯入 Shoplist
  3) Delete + Drop    刪除資料並 DROP 所有 Table（⚠️ 破壞性）
  4) 建立 Table       migrate 建立所有 Table
  5) Import Data      從 data_export.json 匯入資料（還原）

用法：
  python data_manager.py              # 互動選單（可多選）
  python data_manager.py --run 1,3,5  # 直接執行 1、3、5（非互動）
  python data_manager.py --run all    # 全部執行
  python data_manager.py --run 3 --yes   # 執行 Drop，且不詢問確認
"""

import argparse
import json
import re
import sys
from io import StringIO
from pathlib import Path

# ---------- Django 環境初始化 ----------
BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.core.management import call_command  # noqa: E402
from django.db import connection  # noqa: E402

from shops.models import Shoplist  # noqa: E402
from shops.choices import district_choices  # noqa: E402

# ---------- 常數 ----------
RAW_DATA_FILE = "ptcg shops data.txt"   # 原始資料
BACKUP_FILE = "data_export.json"        # 備份 / 還原用的 JSON
CLEANED_FILE = "cleaned_shops.json"     # 清理後的結果

DAY_MAP = {
    "mon": "monday", "tue": "tuesday", "wed": "wednesday",
    "thu": "thursday", "thur": "thursday", "fri": "friday",
    "sat": "saturday", "sun": "sunday",
}
DAY_TOKEN = re.compile(r"(Mon|Tue|Wed|Thur|Thu|Fri|Sat|Sun):", re.IGNORECASE)
FIELD_PREFIXES = ("phone:", "website:", "web:", "time:", "http", "鑑定")

EXPORT_MODELS = [
    "auth.User", "accounts", "shops", "cards", "listings",
    "contacts", "tradings", "decks", "banners", "pages",
]


# ======================================================================
# 工具函式
# ======================================================================
def log_step(title: str) -> None:
    print("\n" + "=" * 62)
    print(f"  {title}")
    print("=" * 62)


def log_ok(msg: str) -> None:
    print(f"  ✅ {msg}")


def log_warn(msg: str) -> None:
    print(f"  ⚠️  {msg}")


def log_error(msg: str) -> None:
    print(f"  ❌ {msg}")


def resolve_path(p: str) -> Path:
    """相對路徑優先找「目前目錄」，找不到就退回「腳本所在目錄」。"""
    path = Path(p)
    if not path.is_absolute() and not path.exists():
        path = BASE_DIR / path
    return path


def parse_days(content: str) -> dict:
    """以星期代碼為界，切出每一天的營業時間。"""
    days = {}
    tokens = list(DAY_TOKEN.finditer(content))
    for idx, m in enumerate(tokens):
        key = m.group(1).lower()
        start = m.end()
        end = tokens[idx + 1].start() if idx + 1 < len(tokens) else len(content)
        days[DAY_MAP[key]] = content[start:end].strip()
    return days


def infer_district(address: str) -> str:
    for key, value in district_choices.items():
        if key in address:
            return value
    return "Unknown"


def normalize_phone(phone: str) -> str:
    return re.sub(r"\s+", "", phone or "").strip()


def normalize_website(website: str) -> str:
    website = (website or "").strip()
    if website and not website.lower().startswith(("http://", "https://")):
        website = "https://" + website
    return website


def normalize_time(value: str) -> str:
    if not value:
        return ""
    value = value.strip()
    return re.sub(r"^(\d{2})(\d{2})(?=\s|~|$)", r"\1:\2", value)


def is_field_line(line: str) -> bool:
    return line.startswith(FIELD_PREFIXES) or bool(DAY_TOKEN.match(line))


# ======================================================================
# 功能 2 用的清理 / 格式化
# ======================================================================
def clean_data(raw_text: str) -> list:
    """清理原始資料：去重、正規化、推斷分區、略過不完整資料。"""
    records = []
    seen_address = set()

    for block in re.split(r"\n\s*\n", raw_text):
        lines = [l.strip() for l in block.splitlines() if l.strip()]
        if not lines or lines[0].startswith("*"):
            continue

        shopname = lines[0].strip()
        addr_lines = []
        i = 1
        while i < len(lines) and not is_field_line(lines[i]):
            addr_lines.append(lines[i])
            i += 1
        address = " ".join(dict.fromkeys(addr_lines)).strip()

        phone = website = ""
        card_identification = False
        day_parts = []
        for j in range(i, len(lines)):
            line = lines[j]
            if line.startswith("phone:"):
                phone = line[6:].strip()
            elif line.startswith(("website:", "web:")):
                website = line.split(":", 1)[1].strip()
            elif line.startswith("鑑定"):
                card_identification = "有" in line
            elif line.startswith("http"):
                website = line.strip()
            elif line.startswith("time:"):
                day_parts.append(line[5:].strip())
            elif DAY_TOKEN.match(line):
                day_parts.append(line.strip())

        if not address or address in seen_address:
            continue
        seen_address.add(address)

        records.append({
            "shopname": shopname,
            "address": address,
            "district": infer_district(address),
            "phone_number": normalize_phone(phone),
            "website": normalize_website(website),
            "days": parse_days(" ".join(day_parts)),
            "card_identification": card_identification,
        })
    return records


def format_records(cleaned: list) -> tuple:
    """轉成 model 欄位結構，並做長度 / 必填驗證。回傳 (formatted, errors)。"""
    formatted, errors = [], []
    for r in cleaned:
        record = {
            "shopname": r["shopname"][:200],
            "address": r["address"][:200],
            "district": r["district"][:50],
            "website": r["website"],
            "phone_number": r["phone_number"][:20],
            "card_identification": bool(r["card_identification"]),
        }
        for field, value in r["days"].items():
            record[field] = normalize_time(value)[:20]

        if not record["shopname"]:
            errors.append(("?", "店名為空"))
            continue
        if not record["address"]:
            errors.append((record["shopname"], "地址為空"))
            continue
        formatted.append(record)
    return formatted, errors


# ======================================================================
# 五大功能
# ======================================================================
def do_export() -> None:
    """1) 導出資料庫到 JSON 備份。"""
    log_step("1) Export Data（導出資料庫）")
    buf = StringIO()
    call_command("dumpdata", *EXPORT_MODELS, indent=2, stdout=buf)
    data = buf.getvalue()
    out = resolve_path(BACKUP_FILE)
    out.write_text(data, encoding="utf-8")
    log_ok(f"已導出 {len(json.loads(data))} 筆 → {out}")


def do_clean() -> None:
    """2) 清理原始資料 → 匯入 Shoplist。"""
    log_step("2) Clean Data（清理原始資料）")
    src = resolve_path(RAW_DATA_FILE)
    if not src.exists():
        log_error(f"找不到原始資料檔：{src}")
        return

    cleaned = clean_data(src.read_text(encoding="utf-8"))
    formatted, fmt_errors = format_records(cleaned)
    log_ok(f"清理出 {len(cleaned)} 筆、格式化 {len(formatted)} 筆、排除 {len(fmt_errors)} 筆")
    for name, reason in fmt_errors:
        log_warn(f"排除「{name}」：{reason}")

    # 儲存清理結果，供人工核對 / admin 檢查
    resolve_path(CLEANED_FILE).write_text(
        json.dumps(formatted, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    log_ok(f"清理結果已存 → {CLEANED_FILE}")

    # 匯入 Shoplist（bulk_create + 依地址去重）
    existing = set(Shoplist.objects.values_list("address", flat=True))
    new_records = [r for r in formatted if r["address"] not in existing]
    created, errors = 0, []
    for i in range(0, len(new_records), 200):
        batch = [Shoplist(**r) for r in new_records[i:i + 200]]
        try:
            Shoplist.objects.bulk_create(batch)
            created += len(batch)
        except Exception as exc:
            log_warn(f"整批失敗（{exc}），改逐筆重試…")
            for obj in batch:
                try:
                    Shoplist.objects.bulk_create([obj])
                    created += 1
                except Exception as e2:
                    errors.append((obj.shopname, str(e2)))
    log_ok(f"匯入完成：新增 {created} 筆、跳過(重複) {len(formatted) - len(new_records)} 筆、失敗 {len(errors)} 筆")
    for name, reason in errors:
        log_error(f"匯入失敗「{name}」：{reason}")


def do_drop(skip_confirm: bool = False) -> None:
    """3) 刪除資料並 DROP 所有 Table（只 drop table、不動 schema，避免權限問題）。"""
    log_step("3) Delete Data + Drop Table（⚠️ 破壞性）")
    if not skip_confirm:
        log_warn("這會 DROP 資料庫所有 Table 並清空所有資料！")
        if input("確定嗎？輸入 yes 繼續：").strip().lower() != "yes":
            log_warn("已取消")
            return

    tables = connection.introspection.table_names()
    if not tables:
        log_warn("沒有可 drop 的 table")
        return
    quoted = ", ".join(connection.ops.quote_name(t) for t in tables)
    with connection.cursor() as cursor:
        cursor.execute(f"DROP TABLE IF EXISTS {quoted} CASCADE")
    log_ok(f"已 DROP {len(tables)} 個 table")


def do_migrate() -> None:
    """4) 建立 Table（migrate）。"""
    log_step("4) 建立 Table（migrate）")
    call_command("migrate", interactive=False)
    log_ok("migrate 完成")


def do_import() -> None:
    """5) 從 JSON 備份匯入資料（還原）。"""
    log_step("5) Import Data（匯入資料）")
    src = resolve_path(BACKUP_FILE)
    if not src.exists():
        log_error(f"找不到備份檔：{src}（請先執行 1) Export Data）")
        return
    call_command("migrate", interactive=False)  # 確保 table 存在（冪等）
    call_command("loaddata", str(src), verbosity=1)
    log_ok(f"已從 {src} 匯入完成")


# ======================================================================
# 選單
# ======================================================================
FUNCTIONS = [
    (1, "Export Data", "導出資料庫 → data_export.json", do_export),
    (2, "Clean Data", "清理原始資料 → 匯入 Shoplist", do_clean),
    (3, "Delete + Drop", "刪除資料並 DROP 所有 Table ⚠️", do_drop),
    (4, "建立 Table", "migrate 建立所有 Table", do_migrate),
    (5, "Import Data", "從 data_export.json 匯入", do_import),
]


def print_menu() -> None:
    print("\n" + "=" * 62)
    print("  PTCG 資料管理員 (Data Manager)")
    print("=" * 62)
    for num, label, desc, _fn in FUNCTIONS:
        print(f"  {num}) {label:<16} {desc}")
    print("  " + "-" * 58)
    print("  6) 全部執行（依 1→5 順序）")
    print("  0) 離開")
    print("  " + "-" * 58)
    print("  請輸入要執行的功能（可多選，例：1,3,5；或 6 全部；0 離開）")


def parse_selection(text: str) -> list:
    """把使用者輸入解析成功能編號列表（支援逗號 / 空白分隔）。"""
    text = text.strip().lower()
    if text in ("0", "exit", "q", "quit"):
        return []
    if text in ("6", "all", "全部"):
        return [f[0] for f in FUNCTIONS]
    nums = []
    for token in re.split(r"[,\s、]+", text):
        if not token:
            continue
        if token.isdigit():
            n = int(token)
            if 1 <= n <= 5:
                nums.append(n)
            else:
                log_warn(f"忽略無效的編號：{token}")
    # 去重並依功能順序排序
    return sorted(set(nums))


def execute(nums: list, skip_confirm: bool = False) -> None:
    if not nums:
        return
    print(f"\n  將依序執行：{nums}")
    for num in nums:
        label, fn = FUNCTIONS[num - 1][1], FUNCTIONS[num - 1][3]
        try:
            if num == 3:
                fn(skip_confirm)
            else:
                fn()
        except Exception as exc:
            log_error(f"功能「{label}」執行失敗：{exc}")
    print("\n  全部執行完畢。\n")


def run_menu() -> None:
    while True:
        print_menu()
        try:
            choice = input("  → ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if parse_selection(choice) == [] and choice.strip().lower() in ("0", "exit", "q", "quit", ""):
            break
        nums = parse_selection(choice)
        if not nums:
            if choice.strip() == "":
                break
            log_warn("輸入無效，請重新輸入")
            continue
        execute(nums)
    print("  已離開資料管理員。\n")


# ======================================================================
# 主程式
# ======================================================================
def main() -> None:
    parser = argparse.ArgumentParser(description="PTCG 資料管理員：導出 / 清理 / Drop / 建Table / 匯入")
    parser.add_argument("--run", default=None,
                        help="直接執行指定功能（逗號分隔，例：1,3,5；或 all）")
    parser.add_argument("--yes", action="store_true", help="執行 Drop 時不詢問確認")
    args = parser.parse_args()

    if args.run:
        nums = parse_selection(args.run)
        if not nums:
            log_error(f"無效的 --run 參數：{args.run}")
            sys.exit(1)
        execute(nums, skip_confirm=args.yes)
    else:
        run_menu()


if __name__ == "__main__":
    main()
