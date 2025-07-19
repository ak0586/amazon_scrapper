# 🏍️ Amazon Product Auto-Poster to Facebook + Telegram

This Python-based automation script:

* Scrapes Amazon India using either a **local scraper** 
* Selects the product with the **lowest price** among scraped results
* Uploads images to **Facebook Page**
* Publishes a product post with caption and hashtags
* Sends a success **notification to Telegram**

---

## 🚀 Features

* ✅ Smart keyword rotation using `keyword_tracker.json`
* ✅ Scrapes product details, images, and price from Amazon
* ✅ Automatically selects the **lowest priced** product
* ✅ Uploads up to 10 images to a Facebook Page
* ✅ Notifies your Telegram bot with post details
* ✅ Supports **backup**, **retry logic**, and **rate limiting**

---

## 📁 Project Structure

```
.
├── amazon_poster.py             # Main script with local scraper
├── external_scraper_poster.py  # Script using external scraper API
├── keyword_tracker.json        # JSON tracker for keyword rotation
├── description.txt             # Optional: custom video/post descriptions
└── hashtag.txt                 # Optional: hashtag list
```

---

## 🔧 Configuration

Edit the following in both scripts:

```python
FB_PAGE_ID = "YOUR_FACEBOOK_PAGE_ID"
FB_TOKEN = "YOUR_FACEBOOK_PAGE_ACCESS_TOKEN"
TELEGRAM_BOT_TOKEN = "YOUR_TELEGRAM_BOT_TOKEN"
TELEGRAM_CHAT_ID = "YOUR_TELEGRAM_CHAT_ID"
ASSOCIATE_TAG = "YOUR_AMAZON_ASSOCIATE_TAG"
SCRAPER_URL = "https://your-external-scraper.com/scrape"  # for API version
```
You can watch tutorials on youtube to generate facebook access token, telegram bot token, telegram chat id,facebook page id.

> 💡 You can generate Facebook access tokens from the [Meta Graph API Explorer](https://developers.facebook.com/tools/explorer/).

---

## 📌 Usage

### Option 1: Local Scraper (Recommended for more control)

```bash
python3 amazon_poster.py
```

---

## 🧠 How It Works

1. **Keyword Rotation**

   * Keywords are stored and rotated from `keyword_tracker.json`.
   * Automatically updates index, last used keyword, and usage count.

2. **Scraping & Selection**

   * Amazon is scraped using dynamic headers, retries, and delays.
   * From all results, the product with the **minimum price** is selected.

3. **Facebook Upload**

   * Up to 10 product images are uploaded (unpublished).
   * A single post is created combining those images.

4. **Telegram Alert**

   * You get notified with product title, price, and link.

---

## ✅ Sample Output

```
🚀 Starting Amazon Product Social Media Poster...
✅ Keyword: saree
✅ Product: Elegant Silk Saree...
✅ Price: ₹799
✅ Images: 5 uploaded
✅ Facebook: Success
✅ Telegram: Success
🎉 Process completed successfully!
```

---

## 📦 Dependencies

* Python 3.7+
* Required libraries:

```bash
pip install requests beautifulsoup4
```

---

## 🔐 Notes

* This script is built for **educational and affiliate automation** purposes.
* Avoid aggressive scraping to comply with Amazon's ToS.
* Facebook and Telegram APIs require valid tokens and permissions.

---
