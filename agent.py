# =====================================================
# FINAL AI AGENT (UNBREAKABLE VERSION)
# Latest WORLD News → Instagram Posts (NO REPEAT)
# =====================================================

print("🌍 World News Instagram Agent Started...\n")

import feedparser
import subprocess
import os
import time
import random
from PIL import Image, ImageDraw, ImageFont
import requests
from io import BytesIO

# ---------------- CONFIG ----------------
OUTPUT_DIR = "output"
SEEN_FILE = "seen_news.txt"
POST_LIMIT = 10

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Load seen news
seen_links = set()
if os.path.exists(SEEN_FILE):
    with open(SEEN_FILE, "r", encoding="utf-8") as f:
        seen_links = set(f.read().splitlines())

# ---------------------------------------
# STEP 1: FETCH LATEST WORLD NEWS
# ---------------------------------------
feed = feedparser.parse(
    "https://news.google.com/rss/search?q=world+news&hl=en-IN&gl=IN&ceid=IN:en"
)

print(f"🔎 Total fetched from Google: {len(feed.entries)}")

# ---------------------------------------
# STEP 2: SAFE AI CAPTION
# ---------------------------------------
def generate_caption(title):
    prompt = f"Write a short Instagram caption with hashtags for this world news:\n{title}"

    try:
        result = subprocess.run(
            ["ollama", "run", "phi3", prompt],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            timeout=20,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )
        if result.stdout.strip():
            return result.stdout.strip()
    except Exception:
        pass

    return f"""🌍 World Update

{title}

Stay informed with the latest global news.
#WorldNews #BreakingNews #Global #International #Update"""

# ---------------------------------------
# STEP 3: KEYWORD EXTRACTION
# ---------------------------------------
def extract_keyword(title):
    keywords = [
        "war", "conflict", "election", "vote", "politics",
        "economy", "finance", "market",
        "technology", "ai", "cyber",
        "space", "rocket", "isro", "nasa",
        "cricket", "football", "sports",
        "india", "china", "russia", "usa"
    ]

    t = title.lower()
    for k in keywords:
        if k in t:
            return k

    return "world"

# ---------------------------------------
# STEP 4: LOCAL POSTER FALLBACK (ALWAYS WORKS)
# ---------------------------------------
def create_local_poster(title, index):
    img = Image.new(
        "RGB",
        (1080, 1080),
        random.choice(["#0f172a", "#1c1c1c", "#1f2933", "#111827"])
    )

    draw = ImageDraw.Draw(img)

    try:
        font_title = ImageFont.truetype("arial.ttf", 50)
        font_footer = ImageFont.truetype("arial.ttf", 30)
    except:
        font_title = ImageFont.load_default()
        font_footer = ImageFont.load_default()

    words = title.split()
    lines, line = [], ""
    for word in words:
        if len(line + word) <= 38:
            line += word + " "
        else:
            lines.append(line)
            line = word + " "
    lines.append(line)

    y = 330
    for l in lines[:6]:
        draw.text((80, y), l, fill="white", font=font_title)
        y += 70

    draw.text((80, 950), "🌍 WORLD NEWS", fill="white", font=font_footer)

    path = f"{OUTPUT_DIR}/news_image_{index}.jpg"
    img.save(path, "JPEG", quality=95)
    return path

# ---------------------------------------
# STEP 5: CREATE POSTER (ONLINE → FALLBACK)
# ---------------------------------------
def create_poster(title, index):
    keyword = extract_keyword(title)
    seed = f"{keyword}-{index}-{int(time.time())}-{random.randint(100,9999)}"
    url = f"https://picsum.photos/seed/{seed}/1080/1080"

    try:
        response = requests.get(
            url,
            timeout=10,
            headers={"User-Agent": "Mozilla/5.0"}
        )
        img = Image.open(BytesIO(response.content)).convert("RGB")

        overlay = Image.new("RGB", img.size, (0, 0, 0))
        img = Image.blend(img, overlay, 0.35)
        draw = ImageDraw.Draw(img)

        try:
            font_title = ImageFont.truetype("arial.ttf", 50)
            font_footer = ImageFont.truetype("arial.ttf", 30)
        except:
            font_title = ImageFont.load_default()
            font_footer = ImageFont.load_default()

        words = title.split()
        lines, line = [], ""
        for word in words:
            if len(line + word) <= 38:
                line += word + " "
            else:
                lines.append(line)
                line = word + " "
        lines.append(line)

        y = 330
        for l in lines[:6]:
            draw.text((80, y), l, fill="white", font=font_title)
            y += 70

        draw.text((80, 950), "🌍 WORLD NEWS", fill="white", font=font_footer)

        path = f"{OUTPUT_DIR}/news_image_{index}.jpg"
        img.save(path, "JPEG", quality=95)
        return path

    except Exception as e:
        print("⚠️ Image download failed, using local poster")
        return create_local_poster(title, index)

# ---------------------------------------
# STEP 6: PROCESS ONLY NEW NEWS
# ---------------------------------------
count = 0

for news in feed.entries:
    if count >= POST_LIMIT:
        break

    if news.link in seen_links:
        continue

    title = news.title
    print(f"\n📰 Processing NEW News {count+1}/{POST_LIMIT}")
    print("Title:", title)

    caption = generate_caption(title)
    image_path = create_poster(title, count + 1)

    with open(f"{OUTPUT_DIR}/caption_{count+1}.txt", "w", encoding="utf-8") as f:
        f.write(caption)

    seen_links.add(news.link)

    print(f"✅ Image saved → {image_path}")
    print(f"✅ Caption saved → caption_{count+1}.txt")

    count += 1
    time.sleep(1)

# Save seen news
with open(SEEN_FILE, "w", encoding="utf-8") as f:
    for link in seen_links:
        f.write(link + "\n")

print("\n🎉 DONE: Latest unique world news posts generated successfully!")
