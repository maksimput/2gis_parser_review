import asyncio
import aiohttp
import csv
import os
from bs4 import BeautifulSoup
from aiogram import Bot, types
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv

REVIEW_ID_FILE = "review_ids.txt"
CSV_FILE = "reviews.csv"

load_dotenv()
BRANCH_URLS = os.getenv("BRANCH_URLS", "").split(",")
API_TOKEN = os.getenv("TG_BOT_TOKEN")
CHANNEL_ID = os.getenv("TG_CHAT_ID")
API_KEY = os.getenv("API_KEY")


####TGBOTINIT
bot = Bot(
    token=API_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

async def send_message(channel_id: int, text: str):
    await bot.send_message(channel_id, text)
    await bot.session.close()
###

# Загрузка существующих RID
def load_existing_ids():
    if not os.path.exists(REVIEW_ID_FILE):
        return set()
    with open(REVIEW_ID_FILE, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f)

# Сохранение новых RID
def save_new_ids(new_ids):
    with open(REVIEW_ID_FILE, "a", encoding="utf-8") as f:
        for rid in new_ids:
            f.write(rid + "\n")

# Добавление новых отзывов в CSV
def save_reviews_to_csv(reviews):
    write_header = not os.path.exists(CSV_FILE)
    with open(CSV_FILE, "a", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["address", "date", "author", "rating", "text"], delimiter=";")
        if write_header:
            writer.writeheader()
        writer.writerows(reviews)

# Получить title страницы
async def get_page_title(session, url):
    try:
        async with session.get(url, headers={"User-Agent": "Mozilla/5.0"}) as resp:
            html = await resp.text()
            soup = BeautifulSoup(html, "html.parser")
            return soup.title.string.strip().removesuffix(" — 2ГИС") 
    except Exception:
        return "Ошибка получения адреса"

# Получение отзывов
async def fetch_reviews(session, url, existing_ids):
    firm_id = url.split("/")[-1]
    address = await get_page_title(session, url)
    print(f"Ищем отзывы предприятия: {address}")
    new_reviews = []
    new_ids = []
    limit = 50
    offset = 0

    while True:
        api_url = f"https://public-api.reviews.2gis.com/2.0/branches/{firm_id}/reviews"
        params = {
            "limit": limit,
            "offset": offset,
            "is_advertiser": "false",
            "fields": "meta.providers,meta.branch_rating,meta.branch_reviews_count,meta.total_count,reviews.hiding_reason,reviews.is_verified,reviews.emojis",
            "without_my_first_review": "false",
            "rated": "true",
            "sort_by": "date_edited",
            "key": API_KEY,
            "locale": "ru_RU"
        }

        try:
            async with session.get(api_url, params=params) as resp:
                data = await resp.json()
                reviews = data.get("reviews", [])
                if not reviews:
                    break

                for review in reviews:
                    rid = review["id"]
                    if rid in existing_ids:
                        return new_reviews, new_ids  # остановка при первом совпадении

                    new_reviews.append({
                        
                        "address": address,
                        "date": review.get("date_edited") or review.get("date_created"),
                        "author": review["user"]["name"],
                        "rating": review.get("rating", ""),
                        "text": review.get("text", "").replace("\n", " ").strip()
                    })
                    new_ids.append(rid)

                offset += limit
        except Exception as e:
            print(f"Ошибка при запросе {url}: {e}")
            break

    return new_reviews, new_ids


async def main():
    existing_ids = load_existing_ids()
    all_new_reviews = []
    all_new_ids = []

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_reviews(session, link, existing_ids) for link in BRANCH_URLS if link.strip()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        for reviews, ids in results:
            all_new_reviews.extend(reviews)
            all_new_ids.extend(ids)

    if all_new_reviews:
        save_reviews_to_csv(all_new_reviews)
        save_new_ids(all_new_ids)
        print(f"Сохранено новых отзывов: {len(all_new_reviews)}")
        await send_message(CHANNEL_ID, f"Сохранено новых отзывов: {len(all_new_reviews)}")
    else:
        print("Новых отзывов не найдено")
        await send_message(CHANNEL_ID, "Новых отзывов не найдено")

if __name__ == "__main__":
    asyncio.run(main())
