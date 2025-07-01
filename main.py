from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests
import random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

HEADERS = {
    "User-Agent":
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Accept":
    "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
    "Connection": "keep-alive",
}

ASSOCIATE_TAG = "ak0586-21"
KEYWORDS = [
    "shoes", "tshirt", "watch", "jeans", "kurti", "laptop", "mobile",
    "sport shoes", "sandals", "sarees", "shirt", "Top & Tshirt"
]


@app.get("/")
def home():
    products=[]
    products.append({
        "keyword": "Kurtas & Kurtis",
        "title": "ANNI DESIGNER Women’s Rayon Blend Kurta with Palazzo Set",
        "asin": "B0DMT61RSM",
        "image":"https://m.media-amazon.com/images/I/51fz-fVBi6L._SY741_.jpg",
        "price": "₹499.00",
        "url": "https://www.amazon.in/dp/B0DMT61RSM?tag=ak0586-21"
    })
    return {
        "message":
        "Amazon Scraper is live! Visit /scrape to get product data.",
        "keyword": "shoes",
        "products": products
    }


@app.get("/scrape")
def scrape_amazon(request: Request):
    # Get keyword from query param or pick random
    keyword = request.query_params.get("keyword")
    if not keyword:
        keyword = random.choice(KEYWORDS)

    search_url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}"

    try:
        res = requests.get(search_url, headers=HEADERS, timeout=30)

        print("URL:", search_url)
        print("Status:", res.status_code)
        print("Length of HTML:", len(res.text))

        # Save page for debugging
        with open("amazon_page.html", "w", encoding="utf-8") as f:
            f.write(res.text)

        soup = BeautifulSoup(res.text, "html.parser")
        products = []

        for item in soup.select('div[data-component-type="s-search-result"]'):
            asin = item.get("data-asin")
            title = item.select_one("h2 span")
            image = item.select_one("img")
            price_whole = item.select_one(".a-price-whole")
            price_frac = item.select_one(".a-price-fraction")

            if not (asin and title and price_whole and image):
                continue

            products.append({
                "keyword":
                keyword,
                "title":
                title.text.strip(),
                "asin":
                asin,
                "image":
                image.get("src") or image.get("data-src"),
                "price":
                f"₹{price_whole.text.strip()}.{price_frac.text.strip() if price_frac else '00'}",
                "url":
                f"https://www.amazon.in/dp/{asin}?tag={ASSOCIATE_TAG}"
            })

            if len(products) >= 5:
                break

        print(f"✅ Scraped {len(products)} products for: {keyword}")
        return {"keyword": keyword, "products": products}

    except Exception as e:
        print(f"❌ Error scraping: {str(e)}")
        return {"error": f"Scraping failed: {str(e)}"}
