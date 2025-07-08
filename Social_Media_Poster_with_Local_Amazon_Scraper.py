#!/usr/bin/env python3
"""
Social Media Poster with Local Amazon Scraper
Posts Amazon products to Facebook and sends Telegram notifications
Modified to select keywords serially using JSON file tracking
"""

import requests
import random
import time
import json
import sys
import os
from typing import Dict, List

# Import the scraper functions from the previous script
# You can either copy the functions here or import them from a separate file
from bs4 import BeautifulSoup
import re
from urllib.parse import urlencode

# === CONFIG ===
FB_PAGE_ID = "104283058702700"
FB_TOKEN = "EAANG2pObL1IBO7yheD2Dipi1CPJS180hBtAZC6ePLKRt9k1uvrbmLOuqDca4Jw96DEq7SvOzZAyUlry9n93p30G3T7LZCzxYih2PAwdTkMV9Rv8ZBOZCWEZAZA9lOmKxaVM5mlyPHG7KUF6U4qQO3mJJIOIcf4Yi5ZBnZAdUGthbYH2PZALTmc4O3SZBZAvpCXjGPEZBBhscZD"
TELEGRAM_BOT_TOKEN = "7331599173:AAGnoNDOTYZGx-C3y_MCu1rtGwosZsdm9tk"
TELEGRAM_CHAT_ID = "2142558647"

# Keyword tracking file
KEYWORD_TRACKER_FILE = "keyword_tracker.json"

# === SCRAPER FUNCTIONS (copied from previous script) ===
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

PROXIES = []
ASSOCIATE_TAG = "ak0586-21"
KEYWORDS = [
    "shoes", "tshirt", "watch", "jeans", "kurti", "laptop", "mobile",
    "sport shoes", "sandals", "sarees", "shirt", "Top & Tshirt","Kurtas & Kurtis","wallet","belt"
]

last_request_time = 0
MIN_DELAY = 2

def load_keyword_tracker():
    """Load keyword tracking data from JSON file"""
    if os.path.exists(KEYWORD_TRACKER_FILE):
        try:
            with open(KEYWORD_TRACKER_FILE, 'r') as f:
                data = json.load(f)
                return data
        except (json.JSONDecodeError, FileNotFoundError):
            print("⚠️ Keyword tracker file corrupted or not found. Creating new one.")
    
    # Create default tracker data
    default_data = {
        "current_index": 0,
        "keywords": KEYWORDS,
        "last_used": None,
        "usage_count": 0
    }
    save_keyword_tracker(default_data)
    return default_data

def save_keyword_tracker(data):
    """Save keyword tracking data to JSON file"""
    try:
        with open(KEYWORD_TRACKER_FILE, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"📝 Keyword tracker saved successfully")
    except Exception as e:
        print(f"⚠️ Failed to save keyword tracker: {str(e)}")

def get_next_keyword():
    """Get the next keyword in serial order"""
    tracker_data = load_keyword_tracker()
    
    current_index = tracker_data["current_index"]
    keywords = tracker_data["keywords"]
    
    # Get current keyword
    selected_keyword = keywords[current_index]
    
    # Update tracker data
    tracker_data["current_index"] = (current_index + 1) % len(keywords)
    tracker_data["last_used"] = selected_keyword
    tracker_data["usage_count"] += 1
    
    # Save updated data
    save_keyword_tracker(tracker_data)
    
    print(f"🎯 Selected keyword: '{selected_keyword}' (Index: {current_index})")
    print(f"📊 Total keywords used so far: {tracker_data['usage_count']}")
    print(f"🔄 Next keyword will be: '{keywords[tracker_data['current_index']]}'")
    
    return selected_keyword

def get_random_headers():
    """Generate random headers for each request"""
    return {
        "User-Agent": random.choice(USER_AGENTS),
        "Accept-Language": random.choice([
            "en-US,en;q=0.9",
            "en-GB,en;q=0.9",
            "en-CA,en;q=0.9"
        ]),
        "Accept-Encoding": "gzip, deflate, br",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0",
        "DNT": "1",
        "Referer": random.choice([
            "https://www.google.com/",
            "https://www.amazon.in/",
            "https://www.bing.com/"
        ])
    }

def rate_limit():
    """Implement rate limiting between requests"""
    global last_request_time
    current_time = time.time()
    time_since_last = current_time - last_request_time
    
    if time_since_last < MIN_DELAY:
        sleep_time = MIN_DELAY - time_since_last + random.uniform(0.5, 2.0)
        time.sleep(sleep_time)
    
    last_request_time = time.time()

def make_request_with_retry(url: str, max_retries: int = 3):
    """Make request with retry logic and different strategies"""
    for attempt in range(max_retries):
        try:
            rate_limit()
            headers = get_random_headers()
            proxies = random.choice(PROXIES) if PROXIES else None
            
            if attempt > 0:
                delay = random.uniform(5, 15) * attempt
                print(f"Retry {attempt}, waiting {delay:.1f} seconds...")
                time.sleep(delay)
            
            session = requests.Session()
            session.headers.update(headers)
            
            if attempt == 0:
                response = session.get(url, proxies=proxies, timeout=30)
            elif attempt == 1:
                cookies = {
                    'session-id': f'session-{random.randint(100000, 999999)}',
                    'ubid-acbin': f'ubid-{random.randint(100000, 999999)}',
                    'x-wl-uid': f'uid-{random.randint(100000, 999999)}'
                }
                response = session.get(url, cookies=cookies, proxies=proxies, timeout=30)
            else:
                params = {
                    'ref': 'sr_pg_1',
                    'qid': str(int(time.time())),
                    'sprefix': 'search'
                }
                response = session.get(url, params=params, proxies=proxies, timeout=30)
            
            print(f"Attempt {attempt + 1}: Status {response.status_code}")
            
            if response.status_code == 200:
                return response
            elif response.status_code == 503:
                print("Service unavailable, waiting longer...")
                time.sleep(random.uniform(10, 20))
            elif response.status_code == 429:
                print("Rate limited, waiting...")
                time.sleep(random.uniform(30, 60))
            else:
                print(f"HTTP {response.status_code}: {response.reason}")
                
        except requests.exceptions.RequestException as e:
            print(f"Request failed on attempt {attempt + 1}: {str(e)}")
            if attempt < max_retries - 1:
                time.sleep(random.uniform(5, 10))
    
    return None

def enhance_image_quality(image_url: str) -> str:
    """Enhance image quality by modifying Amazon image URL parameters"""
    if not image_url:
        return image_url
    
    enhanced_url = image_url
    
    replacements = [
        ('._AC_UY218_', '._AC_UY1000_'),
        ('._AC_UX218_', '._AC_UX1000_'),
        ('._AC_UY200_', '._AC_UY1000_'),
        ('._AC_UX200_', '._AC_UX1000_'),
        ('._AC_UY400_', '._AC_UY1000_'),
        ('._AC_UX400_', '._AC_UX1000_'),
        ('._AC_UY500_', '._AC_UY1000_'),
        ('._AC_UX500_', '._AC_UX1000_'),
        ('._SY160_', '._SY1000_'),
        ('._SX160_', '._SX1000_'),
        ('._SY200_', '._SY1000_'),
        ('._SX200_', '._SX1000_'),
        ('._SY300_', '._SY1000_'),
        ('._SX300_', '._SX1000_'),
        ('._SY400_', '._SY1000_'),
        ('._SX400_', '._SX1000_'),
        ('._SY500_', '._SY1000_'),
        ('._SX500_', '._SX1000_'),
        ('._AC_SY200_', '._AC_SY1000_'),
        ('._AC_SX200_', '._AC_SX1000_'),
        ('._AC_SY400_', '._AC_SY1000_'),
        ('._AC_SX400_', '._AC_SX1000_'),
        ('._AC_SY500_', '._AC_SY1000_'),
        ('._AC_SX500_', '._AC_SX1000_'),
    ]
    
    for old_param, new_param in replacements:
        enhanced_url = enhanced_url.replace(old_param, new_param)
    
    if '._AC_' not in enhanced_url and '._SY' not in enhanced_url and '._SX' not in enhanced_url:
        if '.jpg' in enhanced_url:
            enhanced_url = enhanced_url.replace('.jpg', '._AC_SY1000_.jpg')
        elif '.jpeg' in enhanced_url:
            enhanced_url = enhanced_url.replace('.jpeg', '._AC_SY1000_.jpeg')
        elif '.png' in enhanced_url:
            enhanced_url = enhanced_url.replace('.png', '._AC_SY1000_.png')
    
    return enhanced_url

def get_product_images(asin: str) -> List[str]:
    """Get all product images from Amazon product page"""
    product_url = f"https://www.amazon.in/dp/{asin}"
    
    try:
        print(f"Fetching product page for ASIN: {asin}")
        response = make_request_with_retry(product_url)
        
        if not response:
            print(f"Failed to fetch product page for ASIN: {asin}")
            return []
        
        soup = BeautifulSoup(response.text, "html.parser")
        images = []
        
        # Extract from image gallery scripts
        scripts = soup.find_all('script', type='text/javascript')
        for script in scripts:
            if script.string and 'ImageBlockATF' in script.string:
                image_matches = re.findall(r'"hiRes":"([^"]+)"', script.string)
                for match in image_matches:
                    image_url = match.replace('\\u0026', '&').replace('\\/', '/')
                    if image_url and image_url.startswith('http'):
                        enhanced_url = enhance_image_quality(image_url)
                        images.append(enhanced_url)
        
        # Extract from colorImages data
        for script in scripts:
            if script.string and 'colorImages' in script.string:
                color_matches = re.findall(r'"large":"([^"]+)"', script.string)
                for match in color_matches:
                    image_url = match.replace('\\u0026', '&').replace('\\/', '/')
                    if image_url and image_url.startswith('http'):
                        enhanced_url = enhance_image_quality(image_url)
                        if enhanced_url not in images:
                            images.append(enhanced_url)
        
        # Extract from img tags
        img_selectors = [
            'img[data-old-hires]',
            'img[data-a-hires]',
            'img.a-dynamic-image',
            '#landingImage',
            '.a-dynamic-image',
            '.image-wrapper img'
        ]
        
        for selector in img_selectors:
            img_elements = soup.select(selector)
            for img in img_elements:
                hires_attrs = ['data-old-hires', 'data-a-hires', 'src', 'data-src']
                for attr in hires_attrs:
                    image_url = img.get(attr)
                    if image_url and image_url.startswith('http'):
                        enhanced_url = enhance_image_quality(image_url)
                        if enhanced_url not in images:
                            images.append(enhanced_url)
        
        # Remove duplicates while preserving order
        unique_images = []
        seen = set()
        for img in images:
            if img not in seen:
                seen.add(img)
                unique_images.append(img)
        
        print(f"Found {len(unique_images)} unique images for ASIN: {asin}")
        return unique_images[:10]
        
    except Exception as e:
        print(f"Error fetching images for ASIN {asin}: {str(e)}")
        return []

def parse_products(soup, keyword: str) -> List[Dict]:
    """Parse products from Amazon search results"""
    products = []
    
    selectors = [
        'div[data-component-type="s-search-result"]',
        '.s-result-item[data-asin]',
        '[data-component-type="s-search-result"]'
    ]
    
    items = []
    for selector in selectors:
        items = soup.select(selector)
        if items:
            print(f"Found {len(items)} items with selector: {selector}")
            break
    
    if not items:
        print("No product items found with any selector")
        return products
    
    for item in items:
        try:
            asin = item.get("data-asin")
            if not asin:
                continue
                
            title_selectors = [
                "h2 span",
                ".s-size-mini span",
                "h2 a span",
                ".s-title-instructions-style span"
            ]
            
            title = None
            for selector in title_selectors:
                title_elem = item.select_one(selector)
                if title_elem:
                    title = title_elem.text.strip()
                    break
            
            if not title:
                continue
            
            thumbnail_selectors = [
                "img",
                ".s-image",
                ".s-product-image img"
            ]
            
            thumbnail_image = None
            for selector in thumbnail_selectors:
                img_elem = item.select_one(selector)
                if img_elem:
                    thumbnail_image = img_elem.get("src") or img_elem.get("data-src")
                    if thumbnail_image:
                        thumbnail_image = enhance_image_quality(thumbnail_image)
                        break
            
            print(f"Getting all images for product: {title[:50]}...")
            all_images = get_product_images(asin)
            
            if not all_images and thumbnail_image:
                all_images = [thumbnail_image]
            
            price_selectors = [
                ".a-price-whole",
                ".a-price .a-offscreen",
                ".a-price-range .a-offscreen",
                ".a-price-symbol"
            ]
            
            price = None
            for selector in price_selectors:
                price_elem = item.select_one(selector)
                if price_elem:
                    price_text = price_elem.text.strip()
                    if price_text and '₹' in price_text:
                        price = price_text
                        break
            
            if not price:
                price_whole = item.select_one(".a-price-whole")
                price_frac = item.select_one(".a-price-fraction")
                if price_whole:
                    price = f"₹{price_whole.text.strip()}.{price_frac.text.strip() if price_frac else '00'}"
            
            if title and asin:
                products.append({
                    "keyword": keyword,
                    "title": title,
                    "asin": asin,
                    "images": all_images,
                    "thumbnail": thumbnail_image,
                    "price": price or "Price not available",
                    "url": f"https://www.amazon.in/dp/{asin}?tag={ASSOCIATE_TAG}"
                })
                
                if len(products) >= 5:
                    break
                    
        except Exception as e:
            print(f"Error parsing product: {str(e)}")
            continue
    
    return products

def scrape_amazon_products(keyword: str) -> Dict:
    """Main scraping function - now takes keyword as required parameter"""
    print(f"🔍 Scraping Amazon for: {keyword}")
    
    search_params = {
        'k': keyword,
        'ref': 'sr_pg_1',
        'qid': str(int(time.time())),
        'sprefix': keyword[:3]
    }
    
    search_url = f"https://www.amazon.in/s?{urlencode(search_params)}"
    
    try:
        print(f"Scraping URL: {search_url}")
        
        response = make_request_with_retry(search_url)
        
        if not response:
            return {"error": "Failed to fetch data after multiple attempts"}
        
        print(f"Status: {response.status_code}")
        print(f"Response length: {len(response.text)}")
        
        if "Sorry, we just need to make sure you're not a robot" in response.text:
            return {"error": "Amazon CAPTCHA detected. Please try again later."}
        
        if "To discuss automated access to Amazon data please contact" in response.text:
            return {"error": "Amazon has detected automated access. Please try again later."}
        
        soup = BeautifulSoup(response.text, "html.parser")
        products = parse_products(soup, keyword)
        
        print(f"✅ Scraped {len(products)} products for: {keyword}")
        
        if not products:
            return {
                "keyword": keyword,
                "products": [],
                "message": "No products found. Amazon might be blocking or the page structure changed."
            }
        
        return {"keyword": keyword, "products": products}
        
    except Exception as e:
        print(f"❌ Error scraping: {str(e)}")
        return {"error": f"Scraping failed: {str(e)}"}

def upload_to_facebook(images: List[str], caption: str) -> bool:
    """Upload images to Facebook and create post"""
    print(f"📱 Starting Facebook upload process...")
    
    # Upload images to Facebook (unpublished)
    media_ids = []
    for i, image_url in enumerate(images, 1):
        print(f"📷 Uploading image {i}/{len(images)}: {image_url}")
        
        upload_response = requests.post(
            f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/photos",
            data={
                "access_token": FB_TOKEN,
                "url": image_url,
                "published": "false"
            }
        )
        
        try:
            upload = upload_response.json()
        except:
            print(f"⚠️ Failed to parse upload response for image {i}")
            continue
            
        if "id" in upload:
            media_ids.append({"media_fbid": upload["id"]})
            print(f"✅ Image {i} uploaded successfully")
            time.sleep(2)  # gentle delay between uploads
        else:
            print(f"⚠️ Failed to upload image {i}:", upload)
            # Continue with other images instead of exiting
    
    if not media_ids:
        print("❌ No images uploaded successfully.")
        return False
    
    print(f"📝 Creating Facebook post with {len(media_ids)} images...")
    
    # Create Facebook post with all images
    post_response = requests.post(
        f"https://graph.facebook.com/v19.0/{FB_PAGE_ID}/feed",
        data={
            "access_token": FB_TOKEN,
            "message": caption,
            "attached_media": json.dumps(media_ids)
        }
    )
    
    try:
        post = post_response.json()
    except:
        print("❌ Failed to parse post response")
        return False
    
    if "id" in post:
        print("✅ Post uploaded to Facebook successfully!")
        print(f"📍 Post ID: {post['id']}")
        return True
    else:
        print("❌ Facebook post failed:", post)
        return False

def send_telegram_notification(title: str, price: str, product_url: str) -> bool:
    """Send notification to Telegram"""
    print("📨 Sending Telegram notification...")
    
    telegram_message = f"""✅ Product Posted to Facebook!

🛍️ {title}
💰 {price}
🔗 {product_url}

#AmazonPost #AutoPosted"""
    
    tg_response = requests.get(
        f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage",
        params={
            "chat_id": TELEGRAM_CHAT_ID,
            "text": telegram_message
        }
    )
    
    if tg_response.ok:
        print("✅ Telegram notification sent successfully!")
        return True
    else:
        print("⚠️ Telegram message failed:", tg_response.text)
        return False

def show_keyword_status():
    """Show current keyword tracking status"""
    print("\n=== KEYWORD TRACKING STATUS ===")
    tracker_data = load_keyword_tracker()
    
    print(f"📊 Current Index: {tracker_data['current_index']}")
    print(f"🎯 Next Keyword: '{tracker_data['keywords'][tracker_data['current_index']]}'")
    print(f"📈 Total Usage Count: {tracker_data['usage_count']}")
    print(f"🔄 Last Used: {tracker_data['last_used'] or 'None'}")
    print(f"📝 Available Keywords: {len(tracker_data['keywords'])}")
    
    # Show all keywords with their indices
    print("\n📋 All Keywords:")
    for i, keyword in enumerate(tracker_data['keywords']):
        marker = "→" if i == tracker_data['current_index'] else " "
        print(f"  {marker} {i:2d}: {keyword}")
    print()

def main():
    """Main execution function"""
    print("🚀 Starting Amazon Product Social Media Poster...")
    
    # Show current keyword status
    show_keyword_status()
    
    # Step 1: Get next keyword in serial order
    print("\n=== STEP 1: SELECTING KEYWORD ===")
    keyword = get_next_keyword()
    
    # Step 2: Scrape Amazon products with selected keyword
    print(f"\n=== STEP 2: SCRAPING AMAZON ===")
    data = scrape_amazon_products(keyword)
    
    # Check for errors
    if "error" in data:
        print(f"❌ Scraping failed: {data['error']}")
        sys.exit(1)
    
    products = data.get("products", [])
    if not products:
        print("❌ No products found.")
        sys.exit(1)
    
    # Step 3: Select a random product from the scraped results
    print(f"\n=== STEP 3: SELECTING PRODUCT ===")
    product = random.choice(products)
    print(f"🎯 Selected product: {product['title'][:50]}...")
    
    # Get product details
    images = product.get("images", [])[:10]  # Limit to 10 images
    title = product["title"]
    price = product["price"]
    product_url = product["url"]
    
    if not images:
        print("❌ No images found for selected product.")
        sys.exit(1)
    
    print(f"📷 Found {len(images)} images for the product")
    
    # Step 4: Create caption
    caption = f"""{title} - {keyword}

💰 Price: {price}
🛒 Shop now 👉 {product_url}

#fashion #amazonfinds #facebookpost #reelschallenge #women #shopnow #shoes #flipkart #style #deals #shopping #onlineshopping #{keyword.replace(' ', '')}"""
    
    # Step 5: Upload to Facebook
    print(f"\n=== STEP 4: UPLOADING TO FACEBOOK ===")
    facebook_success = upload_to_facebook(images, caption)
    
    if not facebook_success:
        print("❌ Facebook upload failed.")
        sys.exit(1)
    
    # Step 6: Send Telegram notification
    print(f"\n=== STEP 5: SENDING TELEGRAM NOTIFICATION ===")
    telegram_success = send_telegram_notification(title, price, product_url)
    
    # Final summary
    print(f"\n=== SUMMARY ===")
    print(f"✅ Keyword: {keyword}")
    print(f"✅ Product: {title[:50]}...")
    print(f"✅ Price: {price}")
    print(f"✅ Images: {len(images)} uploaded")
    print(f"✅ Facebook: {'Success' if facebook_success else 'Failed'}")
    print(f"✅ Telegram: {'Success' if telegram_success else 'Failed'}")
    print(f"🎉 Process completed successfully!")

if __name__ == "__main__":
    main()
