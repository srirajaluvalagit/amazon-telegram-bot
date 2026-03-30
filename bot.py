import requests
from bs4 import BeautifulSoup
import time
import os
import feedparser

# ====== TELEGRAM CONFIG ======
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

print("BOT_TOKEN:", BOT_TOKEN)
print("CHAT_ID:", CHAT_ID)

# ====== HEADERS ======
headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-IN,en;q=0.9"
}

# ====== GET DEAL LINKS FROM RSS ======
def get_deal_links():
    feed_url = "https://www.dealsofamerica.com/rss.xml"
    feed = feedparser.parse(feed_url)

    links = []
    for entry in feed.entries[:10]:
        links.append(entry.link)

    return links

# ====== ADD AFFILIATE TAG ======
def add_affiliate_tag(url):
    tag = "srirajsales-21"   # 🔥 PUT YOUR REAL TAG HERE
    if "?" in url:
        return url + f"&tag={tag}"
    else:
        return url + f"?tag={tag}"

# ====== LOAD DEALS ======
urls = get_deal_links()
print("TOTAL DEALS:", len(urls))

# Filter only Amazon links
urls = [u for u in urls if "amazon" in u]

print("FILTERED AMAZON URLS:", len(urls))
print(urls)

# ====== LOAD POSTED ======
try:
    with open("posted.txt", "r") as f:
        posted = set(f.read().splitlines())
except:
    posted = set()

# ====== LOOP ======
for url in urls:

    if url in posted:
        continue

    try:
        res = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(res.text, "html.parser")

        # TITLE
        title_tag = soup.find("span", {"id": "productTitle"})
        title = title_tag.get_text(strip=True) if title_tag else "No title"

        # PRICE
        price_tag = soup.select_one("span.a-price span.a-offscreen")
        price = price_tag.get_text(strip=True) if price_tag else "No price"

        # IMAGE
        img_tag = soup.find("img", {"id": "landingImage"})
        image = img_tag["src"] if img_tag else None

        # 👉 ADD AFFILIATE LINK HERE
        affiliate_url = add_affiliate_tag(url)

        # MESSAGE
        message = f"""
🔥 <b>MEGA DEAL ALERT</b>

📦 {title[:120]}

💰 <b>Price:</b> {price}

⚡ Limited time deal!

🛒 <a href="{affiliate_url}">Buy Now</a>
"""

        # SEND TO TELEGRAM
        if image:
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto",
                data={
                    "chat_id": CHAT_ID,
                    "photo": image,
                    "caption": message,
                    "parse_mode": "HTML"
                }
            )
        else:
            response = requests.post(
                f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
                data={
                    "chat_id": CHAT_ID,
                    "text": message,
                    "parse_mode": "HTML"
                }
            )

        print("TELEGRAM RESPONSE:", response.text)
        print("Posted:", title)

        # SAVE LINK
        with open("posted.txt", "a") as f:
            f.write(url + "\n")

        time.sleep(5)

    except Exception as e:
        print("ERROR:", e)

print("Done!")
