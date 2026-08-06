
import asyncio, hashlib, json, os, re, time
from pathlib import Path
import cloudscraper
from bs4 import BeautifulSoup
from telegram import Bot
from config import TEST_MODE,PAGES

BOT_TOKEN=os.environ["BOT_TOKEN"]
CHAT_ID=os.environ["CHAT_ID"]
STATE="state.json"

bot=Bot(BOT_TOKEN)
scraper=cloudscraper.create_scraper()

MONTHS="январ|феврал|март|апрел|мая|июн|июл|август|сентябр|октябр|ноябр|декабр"
DATE_PATTERNS=[
    re.compile(r"\b\d{1,2}[./]\d{1,2}[./]\d{2,4}\b"),
    re.compile(r"\b\d{1,2}\s+(?:"+MONTHS+r")[а-я]*\s+\d{4}\b",re.I)
]

def load():
    if Path(STATE).exists():
        return json.loads(Path(STATE).read_text(encoding="utf8"))
    return {}

def save(s):
    Path(STATE).write_text(json.dumps(s,ensure_ascii=False,indent=2),encoding="utf8")

def fetch(url):
    for _ in range(5):
        try:
            r=scraper.get(url,timeout=60,headers={"User-Agent":"Mozilla/5.0"})
            r.raise_for_status()
            soup=BeautifulSoup(r.text,"lxml")
            for t in soup(["script","style","noscript"]): t.decompose()
            return re.sub(r"\s+"," ",soup.get_text(" ",strip=True))
        except Exception:
            time.sleep(10)
    return None

def sha(txt): return hashlib.sha256(txt.encode()).hexdigest()

def dates(text):
    out=set()
    for p in DATE_PATTERNS:
        out.update(p.findall(text))
    return sorted(out)

async def main():
    if TEST_MODE:
        await bot.send_message(chat_id=CHAT_ID,text="✅ TEST_MODE=True\nБот работает.")
        return

    state=load()

    for title,url in PAGES:
        txt=fetch(url)
        if not txt:
            continue
        h=sha(txt)
        ds=dates(txt)
        old=state.get(url,{})
        old_dates=set(old.get("dates",[]))
        new_dates=[d for d in ds if d not in old_dates]

        if old and (h!=old.get("hash")):
            msg=f"🏛 СПбГАСУ\n\nИзменения на странице:\n{title}\n"
            if new_dates:
                msg+="\n📅 Новые даты:\n• "+"\n• ".join(new_dates)
            else:
                msg+="\nСтраница изменилась, но новых дат не найдено."
            msg+=f"\n\n{url}"
            await bot.send_message(chat_id=CHAT_ID,text=msg)

        state[url]={"hash":h,"dates":ds}

    save(state)

if __name__=="__main__":
    asyncio.run(main())
