#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
iguanren.eu.org 壁纸数据生成脚本（B 方案：纯自抓，无第三方依赖）
===========================================================
- 抓取必应官方 HPImageArchive（idx=0..7，最近 8 天）
- 合并进 data.json，按日期去重，**全量归档（永不删除，无限攒数据）**
- 图片全部热链 cn.bing.com（缩略图 _400x240 / 4K _UHD），本站零图片存储
- 由 GitHub Actions 每日定时执行

用法：
    python3 scripts/fetch_bing.py              # 抓取并更新 data.json
    python3 scripts/fetch_bing.py --dry-run    # 只打印结果不写文件
依赖：requests（pip install requests）
"""
import argparse
import json
import os
import sys
import time
from datetime import datetime

import requests

BING_API = "https://cn.bing.com/HPImageArchive.aspx"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
MKT = "zh-CN"
IDX_RANGE = range(0, 8)  # 每次抓最近 8 天（idx=0 今天 … idx=7 八天前）
SLEEP = 0.5            # 请求间隔，避免频率限制

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_FILE = os.path.join(ROOT, "data.json")


def fetch_day(idx: int) -> dict | None:
    """抓取指定 idx 的必应壁纸信息，失败返回 None"""
    url = f"{BING_API}?format=js&n=1&idx={idx}&mkt={MKT}"
    try:
        resp = requests.get(url, headers={"User-Agent": UA}, timeout=20)
        if resp.status_code != 200:
            print(f"  idx={idx}: HTTP {resp.status_code}", file=sys.stderr)
            return None
        img = resp.json().get("images", [])[0]
        # enddate 是必应的展示结束日期（即当天日期），用它做日期键
        date = img.get("enddate", "")
        urlbase = img.get("urlbase", "")  # 形如 /th?id=OHR.xxx
        return {
            "date": date,
            "dateLabel": _fmt_date(date),
            "title": img.get("title", ""),
            "copyright": img.get("copyright", ""),
            "copyrightlink": img.get("copyrightlink", ""),
            "urlbase": urlbase,
            "thumb": f"https://cn.bing.com{urlbase}_400x240.jpg",
            "full": f"https://cn.bing.com{urlbase}_UHD.jpg",
        }
    except Exception as e:
        print(f"  idx={idx}: 异常 {e}", file=sys.stderr)
        return None


def _fmt_date(ymd: str) -> str:
    """20260816 -> 2026-08-16"""
    if len(ymd) != 8 or not ymd.isdigit():
        return ymd
    return f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}"


def load_existing() -> list[dict]:
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, encoding="utf-8") as f:
                return json.load(f).get("items", [])
        except Exception as e:
            print(f"data.json 读取失败，重新生成: {e}", file=sys.stderr)
    return []


def main():
    parser = argparse.ArgumentParser(description="抓取必应壁纸生成 data.json")
    parser.add_argument("--dry-run", action="store_true", help="只打印不写文件")
    args = parser.parse_args()

    print(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] 开始抓取 idx=0..7 ...")
    fresh = []
    for idx in IDX_RANGE:
        item = fetch_day(idx)
        if item:
            fresh.append(item)
        time.sleep(SLEEP)

    if not fresh:
        print("本次抓取全部失败，保留原 data.json", file=sys.stderr)
        sys.exit(1)

    # 合并：新抓的覆盖同日期旧记录，其余保留；全量归档，不裁剪
    old_items = load_existing()
    merged = {item["date"]: item for item in old_items}
    for item in fresh:
        merged[item["date"]] = item
    items = sorted(merged.values(), key=lambda x: x["date"], reverse=True)
    kept = items
    today = datetime.now().strftime("%Y%m%d")
    print(f"合并后 {len(items)} 条（全量归档，无限攒数据）")
    for it in kept[:8]:
        print(f"  {it['date']} | {it['title'][:30]} | {it['full']}")

    # 无变化则跳过写入（避免 Actions 空提交）
    if kept == old_items and os.path.exists(DATA_FILE):
        print("数据无变化，跳过写入")
        return

    payload = {
        "updated": datetime.now().strftime("%Y-%m-%dT%H:%M:%S+08:00"),
        "today": today,
        "count": len(kept),
        "items": kept,
    }

    if args.dry_run:
        print(json.dumps(payload, ensure_ascii=False, indent=2)[:800])
        return

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
    print(f"已写入 {DATA_FILE}（{len(kept)} 条）")


if __name__ == "__main__":
    main()
