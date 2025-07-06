import requests
import random
import time
import json

# === CONFIG ===
SCRAPER_URL = "https://amazon-scrapper-api-f42g.onrender.com/scrape"
FB_PAGE_ID = "104283058702700"
FB_TOKEN = "EAANG2pObL1IBOzBtXXfymywqPXOLCpbpQa9ZAZBBfJqc3PLoIEmKrU2G9QT4zh0lki8KSkHkSP07FQpBzUm6EawYDnbrqoA68c3wDuutGmE2BQZCA1CvuHoHSnNZCpWE8u9DzX3zkyBVc70ForcZBZCCWOexcuHoCIPq6CBfE6x9kf9CbvL8bh73T9EtVJMqkxBII81ovpmZBYNXEA4z5g1OGBjLMfm01vYQ3CkoGRT"
TELEGRAM_BOT_TOKEN = "7331599173:AAGnoNDOTYZGx-C3y_MCu1rtGwosZsdm9tk"
TELEGRAM_CHAT_ID = "2142558647"

# === Scrape Products ===
res = requests.get(SCRAPER_URL)
data = res.json()
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
