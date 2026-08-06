# SPBGASU Monitor v3

## Первичная проверка

1. Загрузите весь проект в GitHub.
2. Добавьте Secrets:
   - BOT_TOKEN
   - CHAT_ID
3. В config.py оставьте TEST_MODE=True.
4. Запустите Actions → Run workflow.
5. Должно прийти сообщение в Telegram.

## После проверки

Измените:

TEST_MODE = False

Сохраните изменения.

После этого бот будет проверять сайт каждые 6 часов.