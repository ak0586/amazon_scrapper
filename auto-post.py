import requests
import random
import time
import json

# === CONFIG ===
SCRAPER_URL = "https://amazon-scrapper-api-f42g.onrender.com/scrape"
FB_PAGE_ID = "104283058702700"
FB_TOKEN = "EAANG2pObL1IBO7yheD2Dipi1CPJS180hBtAZC6ePLKRt9k1uvrbmLOuqDca4Jw96DEq7SvOzZAyUlry9n93p30G3T7LZCzxYih2PAwdTkMV9Rv8ZBOZCWEZAZA9lOmKxaVM5mlyPHG7KUF6U4qQO3mJJIOIcf4Yi5ZBnZAdUGthbYH2PZALTmc4O3SZBZAvpCXjGPEZBBhscZD"
TELEGRAM_BOT_TOKEN = "7331599173:AAGnoNDOTYZGx-C3y_MCu1rtGwosZsdm9tk"
TELEGRAM_CHAT_ID = "2142558647"

# === Wake up the Render server ===
print("🚀 Triggering Render app to wake up...")
try:
    ping = requests.get(BASE_URL, timeout=10)
    print(f"✅ Wake-up ping status: {ping.status_code}")
except Exception as e:
    print(f"⚠️ Wake-up ping failed: {e}")

# === Wait for 5 minutes ===
print("⏳ Waiting 5 minutes for Render to fully wake up...")
time.sleep(300)

# === Now request the actual scraping ===
print("🔍 Requesting scraped products...")
try:
    res = requests.get(SCRAPER_URL, timeout=10)
    data = res.json()
except Exception as e:
    print("❌ Failed to decode JSON from scraper.")
    print("Status Code:", res.status_code)
    print("Raw Text:", res.text)
    print("Error:", e)
    exit(1)

products = data.get("products", [])

if not products:
    print("❌ No products found.")
    exit(1)

product = random.choice(products)
images = product.get("images", [])[:10]  # Limit to 10 images
title = product["title"]
price = product["price"]
product_url = product["url"]
caption = f"""{title} - {product['keyword']}
Price: {price}

Shop now 👉 {product_url}

#fashion #amazonfinds #facebookpost #reelschallenge #women #shopnow #shoes #flipkart #style"""

# === Upload images to Facebook (unpublished) ===
media_ids = []

for image_url in images:
    print(f"📷 Uploading image: {image_url}")
    upload = requests.post(
        f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos",
        data={
            "access_token": FB_TOKEN,
            "url": image_url,
            "published": "false"
        }
    ).json()

    if "id" in upload:
        media_ids.append({"media_fbid": upload["id"]})
        time.sleep(2)  # gentle delay between uploads
    else:
        print("⚠️ Failed to upload image:", upload)
        exit(1)

if not media_ids:
    print("❌ No images uploaded.")
    exit(1)

# === Create Facebook post with all images ===
post = requests.post(
    f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed",
    data={
        "access_token": FB_TOKEN,
        "message": caption,
        "attached_media": json.dumps(media_ids)
    }
).json()

if "id" in post:
    print("✅ Post uploaded to Facebook successfully!")
else:
    print("❌ Facebook post failed:", post)
    exit(1)

# === Send Telegram notification ===
telegram_message = f"✅ Product Posted to Facebook!\n\n🛍️ {title}\n💰 {price}\n🔗 {product_url}"

tg_res = requests.get(
    f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
    params={
        "chat_id": TELEGRAM_CHAT_ID,
        "text": telegram_message
    }
)

if tg_res.ok:
    print("📨 Telegram notification sent.")
else:
    print("⚠️ Telegram message failed:", tg_res.text)
