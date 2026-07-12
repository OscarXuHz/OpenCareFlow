"""Mock 數據生成 — 用 PIL 合成 20 張港式志工探訪紙本表照片。

刻意做出：
- 略傾斜 (-3° ~ 3°)
- 輕微背景紋路 (模擬紙張)
- 手寫風字型 (用 fallback 字型加 italic)
- 不同筆跡顏色 (黑/藍/黑藍混合)
- 邊角陰影
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path
from typing import Sequence

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from ..config import settings


# 候選字型（按優先順序）— 容器內裝了 fonts-noto-cjk
FONT_CANDIDATES = [
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
    "/usr/share/fonts/truetype/noto/NotoSansCJK-Regular.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/System/Library/Fonts/STHeiti Medium.ttc",
    "/Library/Fonts/Arial Unicode.ttf",
    "/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc",
]

HANDWRITE_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Songti.ttc",
    "/System/Library/Fonts/PingFang.ttc",
    "/usr/share/fonts/opentype/noto/NotoSerifCJK-Regular.ttc",
]


def _find_font(candidates: Sequence[str], size: int) -> ImageFont.FreeTypeFont:
    for p in candidates:
        if Path(p).exists():
            try:
                return ImageFont.truetype(p, size=size)
            except OSError:
                continue
    # 最後退回預設 (英文，CJK 顯示為方框，仍可生成圖)
    return ImageFont.load_default()


# ── 合成數據池（明確不對應任何真實人物、電話、地址或機構）──────────────
ELDERS = [
    (
        f"示例長者{i:02d}",
        "女" if i % 2 else "男",
        70 + i,
        "0000 0000",
        f"示例區示例街 {i} 號示例大廈",
    )
    for i in range(1, 21)
]

VOLUNTEERS = [f"示例義工{i:02d}" for i in range(1, 9)]
TEAMS = ["示例義工隊甲", "示例義工隊乙", "示例實習小組", "示例社區小組"]
MOODS = ["良好", "一般", "低落", "焦慮"]
HEALTH = [
    "高血壓控制中", "膝關節痛, 失眠", "糖尿病, 視力下降", "輕度認知障礙",
    "近期失去配偶, 情緒低落", "腰背痛", "聽力下降", "頻尿"
]
FOLLOWUPS = [
    "建議轉介物理治療", "下週覆診陪同", "情緒支援, 連絡社工跟進",
    "安排家居安全評估", "邀請參加中心活動", "",
]


def generate_one(idx: int, out_dir: Path) -> Path:
    """生成一張 A4 比例 (840 x 1188) 的志工探訪表照片。"""
    random.seed(idx + 100)
    W, H = 840, 1188
    bg = (252, 250, 244)  # 米白
    img = Image.new("RGB", (W, H), bg)

    # 加紙張紋路：很淡的隨機點
    noise = Image.effect_noise((W, H), 12).convert("RGB")
    img = Image.blend(img, noise, 0.05)

    draw = ImageDraw.Draw(img)
    title_font = _find_font(FONT_CANDIDATES, 32)
    label_font = _find_font(FONT_CANDIDATES, 18)
    handwrite_font = _find_font(HANDWRITE_CANDIDATES, 22)

    # ── 表頭 ─────────────────────────────────────────────────────────────
    draw.text((W // 2 - 200, 30), "志工長者探訪紀錄表", font=title_font, fill=(20, 30, 60))
    draw.line((40, 90, W - 40, 90), fill=(20, 30, 60), width=3)
    draw.text((50, 100), "（請以正楷填寫）", font=label_font, fill=(80, 80, 80))

    # ── 表格：兩欄 × N 列 ────────────────────────────────────────────────
    elder = ELDERS[idx % len(ELDERS)]
    name, gender, age, phone, address = elder
    volunteer = random.choice(VOLUNTEERS)
    team = random.choice(TEAMS)
    visit_d = date(2026, 5, 1) + timedelta(days=random.randint(0, 11))
    mood = random.choice(MOODS)
    health = random.choice(HEALTH)
    living_alone = random.choice(["是", "否"])
    duration = random.choice([30, 35, 40, 45, 50, 60])
    follow_up_needed = "是" if mood != "良好" else random.choice(["是", "否"])
    follow_up_note = random.choice(FOLLOWUPS) if follow_up_needed == "是" else ""

    rows = [
        ("長者姓名", name),
        ("性別", gender),
        ("年齡", str(age)),
        ("聯絡電話", phone),
        ("地址", address),
        ("獨居", living_alone),
        ("探訪日期", visit_d.isoformat()),
        ("志工姓名", volunteer),
        ("志工隊", team),
        ("探訪時長 (分鐘)", str(duration)),
        ("情緒狀態", mood),
        ("健康關注", health),
        ("需要跟進", follow_up_needed),
        ("跟進備註", follow_up_note or "—"),
    ]

    table_top = 150
    row_h = 64
    label_x = 60
    value_x = 280
    line_color = (60, 80, 130)

    # 外框
    draw.rectangle(
        (40, table_top - 10, W - 40, table_top + row_h * len(rows) + 10),
        outline=line_color, width=2,
    )

    handwrite_colors = [(20, 30, 80), (10, 60, 160), (40, 40, 40)]
    for i, (label, value) in enumerate(rows):
        y = table_top + i * row_h
        # 列分隔線
        if i > 0:
            draw.line((40, y, W - 40, y), fill=line_color, width=1)
        # 標籤 / 值分隔線
        draw.line((value_x - 20, y, value_x - 20, y + row_h), fill=line_color, width=1)
        # 印刷體標籤
        draw.text((label_x, y + 18), label, font=label_font, fill=(30, 30, 30))
        # 手寫體值（隨機顏色、微微偏移）
        color = random.choice(handwrite_colors)
        offset_x = random.randint(-2, 4)
        offset_y = random.randint(-3, 5)
        draw.text((value_x + offset_x, y + 18 + offset_y), value, font=handwrite_font, fill=color)

    # ── 簽名欄 ───────────────────────────────────────────────────────────
    sign_y = table_top + row_h * len(rows) + 40
    draw.text((60, sign_y), "志工簽署：", font=label_font, fill=(30, 30, 30))
    draw.line((180, sign_y + 25, 360, sign_y + 25), fill=(60, 80, 130), width=1)
    draw.text((190, sign_y - 5), volunteer, font=handwrite_font, fill=random.choice(handwrite_colors))
    draw.text((420, sign_y), "日期：", font=label_font, fill=(30, 30, 30))
    draw.line((500, sign_y + 25, 720, sign_y + 25), fill=(60, 80, 130), width=1)
    draw.text((510, sign_y - 5), visit_d.isoformat(), font=handwrite_font, fill=random.choice(handwrite_colors))

    # ── 模擬紙張陰影 + 略傾斜 ───────────────────────────────────────────
    img = img.filter(ImageFilter.SMOOTH)
    rotation = random.uniform(-2.5, 2.5)
    img = img.rotate(rotation, resample=Image.BICUBIC, fillcolor=(245, 245, 240), expand=False)

    out_path = out_dir / f"volunteer_form_{idx:02d}.jpg"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "JPEG", quality=88)
    return out_path


def generate_samples(count: int = 20) -> list[Path]:
    """確保 asset/mock_forms/ 下存在 N 張照片。若已存在則直接回傳，不重新生成。

    這個資料夾屬於後端內部資源，不會經由 /api/files 對外暴露。
    """
    out_dir = settings.asset_path / "mock_forms"
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i in range(count):
        p = out_dir / f"volunteer_form_{i:02d}.jpg"
        if not p.exists():
            paths.append(generate_one(i, out_dir))
        else:
            paths.append(p)
    return paths
