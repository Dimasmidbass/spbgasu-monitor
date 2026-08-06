import asyncio, hashlib, json, os, re, time
from pathlib import Path

import cloudscraper
from bs4 import BeautifulSoup
from telegram import Bot
from config import TEST_MODE, PAGES

BOT_TOKEN=os.environ["BOT_TOKEN"]
CHAT_ID=os.environ["CHAT_ID"]
STATE_FILE="state.json"

bot=Bot(BOT_TOKEN)
scraper=cloudscraper.create_scraper()

def load_state():
    if Path(STATE_FILE).exists():
        return json.loads(Path(STATE_FILE).read_text(encoding="utf8"))
    return {}

def save_state(s):
    Path(STATE_FILE).write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf8")

def fetch(url):
    for _ in range(5):
        try:
            r=scraper.get(url,timeout=60,headers={"User-Agent":"Mozilla/5.0"})
            r.raise_for_status()
            soup=BeautifulSoup(r.text,"lxml")
            for t in soup(["script","style","noscript"]):
                t.decompose()
            return re.sub(r"\s+"," ",soup.get_text(" ",strip=True))
        except Exception as e:
            print(e)
            time.sleep(10)
    return None

def sha(txt):
    return hashlib.sha256(txt.encode()).hexdigest()

async def main():
    if TEST_MODE:
        await bot.send_message(chat_id=CHAT_ID,
                               text="✅ Тестовое сообщение.\nGitHub Actions и Telegram работают.")
        return

    state=load_state()

    for title,url in PAGES:
        text=fetch(url)
        if text is None:
            continue

        h=sha(text)

        if url in state and state[url]!=h:
            await bot.send_message(
                chat_id=CHAT_ID,
                text=f"🔔 Обнаружены изменения:\n\n{title}\n{url}"
            )

        state[url]=h

    save_state(state)

if __name__=="__main__":
    asyncio.run(main())