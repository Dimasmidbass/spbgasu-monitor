import hashlib
import json
import os
import re
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from telegram import Bot

PAGES = [
    (
        "Дни открытых дверей",
        "https://www.spbgasu.ru/applicants/dni-otkrytykh-dverey/",
    ),
    (
        "Дизайн архитектурной среды",
        "https://www.spbgasu.ru/applicants/areas-of-training/dizayn-arkhitekturnoy-sredy/",
    ),
]

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

STATE_FILE = "state.json"

bot = Bot(BOT_TOKEN)


def load_state():
    if Path(STATE_FILE).exists():
        with open(STATE_FILE, "r", encoding="utf8") as f:
            return json.load(f)
    return {}


def save_state(state):
    with open(STATE_FILE, "w", encoding="utf8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)


def get_text(url):
    r = requests.get(
        url,
        timeout=30,
        headers={
            "User-Agent": "Mozilla/5.0"
        },
    )
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "lxml")

    # удаляем мусор
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()

    text = soup.get_text(" ", strip=True)

    # убираем лишние пробелы
    text = re.sub(r"\s+", " ", text)

    return text


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def find_dates(text):
    pattern = r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b"
    return sorted(set(re.findall(pattern, text)))


def important(text):

    words = [
        "07.03.03",
        "дизайн архитектурной среды",
        "архитектур",
        "день открытых дверей",
        "регистрация",
    ]

    low = text.lower()

    found = []

    for w in words:
        if w in low:
            found.append(w)

    return found


async def notify(message):
    await bot.send_message(
        chat_id=CHAT_ID,
        text=message,
    )


async def main():

    state = load_state()

    for title, url in PAGES:

        text = get_text(url)

        h = sha(text)

        if url not in state:

            state[url] = h
            continue

        if state[url] != h:

            dates = find_dates(text)
            words = important(text)

            msg = f"""🔔 СПбГАСУ

Изменилась страница:

{title}

Совпадения:
{', '.join(words) if words else 'нет'}

Даты:
{', '.join(dates) if dates else 'не найдены'}

{url}
"""

            await notify(msg)

            state[url] = h

    save_state(state)


if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
