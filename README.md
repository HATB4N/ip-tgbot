# ip-tgbot
DDNS is the best invention ever

A Telegram bot for server IP monitoring (DDNS backup).

- Check your current public IP address
- Get notifications when your IP changes

## Install & Run
```bash
git clone https://HATB4N/ip-tgbot.git

cd ip-tgbot

docker build -t ip-tgbot .

docker run -d --name ip-tgbot --restart=always --env-file .env ip-tgbot
```
