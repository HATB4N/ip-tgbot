# ip tgbot
ddns is best invention ever

## install & run
```bash
git clone https://HATB4N/ipcheck.git

cd ipcheck

docker build -t ip-tgbot .

docker run -d --name ip-tgbot --restart=always --env-file .env ip-tgbot
```