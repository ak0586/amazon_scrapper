from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import random
import time
import json
from typing import List, Dict
from urllib.parse import urlencode

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

# Rotate between multiple user agents
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/120.0.0.0 Safari/537.36"
]

# Proxy list (add your proxy servers here)
PROXIES = [
    # Example: {"http": "http://proxy1:port", "https": "https://proxy1:port"},
    # Add your proxy servers here
]

ASSOCIATE_TAG = "ak0586-21"
KEYWORDS = [
    "shoes", "tshirt", "watch", "jeans", "kurti", "laptop", "mobile",
    "sport shoes", "sandals", "sarees", "shirt", "Top & Tshirt","Kurtas & Kurtis","wallet","belt"
]

# Rate limiting
last_request_time = 0
MIN_DELAY = 2  # Minimum delay between requests in seconds

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
            rate_limit()  # Apply rate limiting
            
            headers = get_random_headers()
            proxies = random.choice(PROXIES) if PROXIES else None
            
            # Add random delay between attempts
            if attempt > 0:
                delay = random.uniform(5, 15) * attempt
                print(f"Retry {attempt}, waiting {delay:.1f} seconds...")
                time.sleep(delay)
            
            session = requests.Session()
            session.headers.update(headers)
            
            # Try different request strategies
            if attempt == 0:
                # Standard request
                response = session.get(url, proxies=proxies, timeout=30)
            elif attempt == 1:
                # Request with cookies (simulate browsing session)
                cookies = {
                    'session-id': f'session-{random.randint(100000, 999999)}',
                    'ubid-acbin': f'ubid-{random.randint(100000, 999999)}',
                    'x-wl-uid': f'uid-{random.randint(100000, 999999)}'
                }
                response = session.get(url, cookies=cookies, proxies=proxies, timeout=30)
            else:
                # Request with additional parameters
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

def parse_products(soup, keyword: str) -> List[Dict]:
    """Parse products from Amazon search results"""
    products = []
    
    # Try multiple selectors as Amazon changes them frequently
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
                
            # Try multiple title selectors
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
            
            # Try multiple image selectors
            image_selectors = [
                "img",
                ".s-image",
                ".s-product-image img"
            ]
            
            image_url = None
            for selector in image_selectors:
                img_elem = item.select_one(selector)
                if img_elem:
                    image_url = img_elem.get("src") or img_elem.get("data-src")
                    if image_url:
                        break
            
            # Try multiple price selectors
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
            
            # If no price found, try different approach
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
                    "image": image_url,
                    "price": price or "Price not available",
                    "url": f"https://www.amazon.in/dp/{asin}?tag={ASSOCIATE_TAG}"
                })
                
                if len(products) >= 5:
                    break
                    
        except Exception as e:
            print(f"Error parsing product: {str(e)}")
            continue
    
    return products

@app.get("/")
def home():
    products = []
    products.append({
        "keyword": "Kurtas & Kurtis",
        "title": "ANNI DESIGNER Women's Rayon Blend Kurta with Palazzo Set",
        "asin": "B0DMT61RSM",
        "image": "https://m.media-amazon.com/images/I/51fz-fVBi6L._SY741_.jpg",
        "price": "₹499.00",
        "url": "https://www.amazon.in/dp/B0DMT61RSM?tag=ak0586-21"
    })
    return {
        "message": "Enhanced Amazon Scraper is live! Visit /scrape to get product data.",
        "keyword": "shoes",
        "products": products
    }

@app.get("/scrape")
def scrape_amazon(request: Request):
    # Get keyword from query param or pick random
    keyword = request.query_params.get("keyword")
    if not keyword:
        keyword = random.choice(KEYWORDS)
    
    # Build search URL with additional parameters
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
        
        # Save page for debugging
        with open("amazon_page.html", "w", encoding="utf-8") as f:
            f.write(response.text)
        
        # Check for common blocking indicators
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

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": time.time()}

@app.get("/test-headers")
def test_headers():
    """Test endpoint to see what headers are being used"""
    headers = get_random_headers()
    return {"headers": headers}
