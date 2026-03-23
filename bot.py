import requests
from bs4 import BeautifulSoup
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

# ====== HEADERS ======
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept-Language": "en-IN,en;q=0.9"
}

# ====== SEARCH URL ======
search_url = "https://www.amazon.in/s?k=mobile+deals"

# ====== GET PRODUCT LINKS ======
def get_product_links(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []
    for a in soup.select("a.a-link-normal.s-no-outline"):
        href = a.get("href")
        if href and "/dp/" in href:
            full_link = "https://www.amazon.in" + href.split("?")[0]
            links.append(full_link)

    return list(set(links))

urls = get_product_links(search_url)[:5]  # limit to 5

# ====== LOAD POSTED LINKS ======
try:
    with open("posted.txt", "r") as f:
        posted = set(f.read().splitlines())
except:
    posted = set()

# ====== TELEGRAM URL ======
send_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# ====== LOOP ======
for url in urls:

    if url in posted:
        continue

    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # ====== TITLE ======
    title_tag = soup.find("span", {"id": "productTitle"})
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"

    # ====== PRICE ======
    price_tag = soup.select_one("span.a-price span.a-offscreen")
    price = price_tag.get_text(strip=True) if price_tag else "Price not found"

    # ====== IMAGE ======
    img_tag = soup.find("img", {"id": "landingImage"})
    image = img_tag["src"] if img_tag else None

    # ====== MESSAGE ======
    message = f"""
🔥 *MEGA DEAL ALERT* 🔥

📦 *{title}*

💰 *Price:* {price}

🛒 [Buy Now]({url})
"""

    # ====== SEND ======
    if image:
        requests.post(f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto", data={
            "chat_id": CHAT_ID,
            "photo": image,
            "caption": message,
            "parse_mode": "Markdown"
        })
    else:
        requests.post(send_url, data={
            "chat_id": CHAT_ID,
            "text": message,
            "parse_mode": "Markdown"
        })

    print(f"Posted: {title}")

    # ====== SAVE ======
    with open("posted.txt", "a") as f:
        f.write(url + "\n")

    time.sleep(5)

print("Done!")
