import asyncio, hashlib, json, os, re, time
from pathlib import Path
import cloudscraper
from bs4 import BeautifulSoup
from telegram import Bot

PAGES=[
("Дни открытых дверей","https://www.spbgasu.ru/applicants/dni-otkrytykh-dverey/"),
("Дизайн архитектурной среды","https://www.spbgasu.ru/applicants/areas-of-training/dizayn-arkhitekturnoy-sredy/")
]

BOT_TOKEN=os.environ["BOT_TOKEN"]
CHAT_ID=os.environ["CHAT_ID"]
STATE="state.json"
bot=Bot(BOT_TOKEN)
scraper=cloudscraper.create_scraper()

def load():
    return json.loads(Path(STATE).read_text(encoding="utf8")) if Path(STATE).exists() else {}
def save(s):
    Path(STATE).write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf8")

def get_text(url):
    for i in range(5):
        try:
            r=scraper.get(url,timeout=90,headers={"User-Agent":"Mozilla/5.0"})
            r.raise_for_status()
            soup=BeautifulSoup(r.text,"lxml")
            for t in soup(["script","style","noscript"]): t.decompose()
            return re.sub(r"\s+"," ",soup.get_text(" ",strip=True))
        except Exception as e:
            print(e)
            time.sleep(15)
    return None

def h(x): return hashlib.sha256(x.encode()).hexdigest()

async def main():
    st=load()
    for title,url in PAGES:
        text=get_text(url)
        if text is None:
            print("Skip",url)
            continue
        hh=h(text)
        old=st.get(url)
#        if old and old!=hh:
#            await bot.send_message(CHAT_ID,f"🔔 Изменения на странице:\n{title}\n{url}")
await bot.send_message(
    chat_id=CHAT_ID,
    text=f"""✅ Тест

Бот работает!

Страница:
{title}

Время проверки прошло успешно.
"""
)    
st[url]=hh
save(st)

asyncio.run(main())
