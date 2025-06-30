from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from bs4 import BeautifulSoup
import requests, random

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"])

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
    "Accept-Language": "en-US,en;q=0.9",
}

ASSOCIATE_TAG = "ak0586-21"
KEYWORDS = ["shoes", "tshirt", "watch", "jeans", "kurti", "backpack"]


@app.get("/scrape")
def scrape_amazon():
    keyword = random.choice(KEYWORDS)
    url = f"https://www.amazon.in/s?k={keyword.replace(' ', '+')}"
    res = requests.get(url, headers=HEADERS)
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    for item in soup.select(".s-result-item[data-asin]"):
        asin = item.get("data-asin")
        title = item.select_one("h2 span")
        image = item.select_one("img")
        price_whole = item.select_one(".a-price-whole")
        price_frac = item.select_one(".a-price-fraction")

        if not (asin and title and price_whole and image):
            continue

        results.append({
            "title":
            title.text.strip(),
            "asin":
            asin,
            "image":
            image["src"],
            "price":
            f"₹{price_whole.text.strip()}.{price_frac.text.strip() if price_frac else '00'}",
            "url":
            f"https://www.amazon.in/dp/{asin}?tag={ASSOCIATE_TAG}"
        })
        if len(results) >= 10:
            break

    return {"keyword": keyword, "products": results}
