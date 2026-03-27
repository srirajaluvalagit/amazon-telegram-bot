import requests
from bs4 import BeautifulSoup
import time
import os

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

headers = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-IN,en;q=0.9"
}

# ====== SEARCH PAGE ======
search_url = "https://www.amazon.in/s?k=mobile+deals"

# ====== GET PRODUCT LINKS ======
def get_product_links(url):
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    links = []

    for a in soup.find_all("a", href=True):
        href = a["href"]

        if "/dp/" in href:
            clean = "https://www.amazon.in" + href.split("?")[0]
            links.append(clean)

    return list(set(links))


urls = get_product_links(search_url)[:5]

print("TOTAL URLS FOUND:", len(urls))
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

    res = requests.get(url, headers=headers)
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

    # MESSAGE (HTML SAFE)
    message = f"""
🔥 <b>MEGA DEAL ALERT</b>

📦 {title}

💰 Price: {price}

🛒 <a href="{url}">Buy Now</a>
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

print("Done!")
