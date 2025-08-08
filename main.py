import hashlib
import os
import asyncio
import httpx
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
)

TOKEN = os.getenv("TOKEN")
PW_HASH = os.getenv("PW_HASH")

CHAT_IDS = set()
LISTEN_IDS = set()

def isValid(chat_id):
    return chat_id in CHAT_IDS

async def get_ip():
    async with httpx.AsyncClient(timeout=5) as client:
        r = await client.get("https://ipinfo.io/ip")
        r.raise_for_status()
        return r.text.strip()

async def ip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not isValid(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="invalid auth data")
        return
    send_msg = await get_ip()
    await context.bot.send_message(chat_id = chat_id, text = send_msg)

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not isValid(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="invalid auth data")
        return
    await context.bot.send_message(chat_id = chat_id, text = "verified auth data")

async def auth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("format: /auth <password>")
        return
    if hashlib.sha256(context.args[0].encode()).hexdigest() == PW_HASH:
        CHAT_IDS.add(update.effective_chat.id)
        await context.bot.send_message(chat_id=update.effective_chat.id, text = "authorized successfully")
    else:
        await context.bot.send_message(chat_id=update.effective_chat.id, text="authorized failed")
    await update.message.delete()

async def register(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not isValid(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="invalid auth data")
        return
    LISTEN_IDS.add(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="registered successfully")

async def unregister(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    if not isValid(chat_id):
        await context.bot.send_message(chat_id=chat_id, text="invalid auth data")
        return
    LISTEN_IDS.remove(chat_id)
    await context.bot.send_message(chat_id=chat_id, text="unregistered successfully")

async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help = ("/help: show help\n"
            "/status: show auth status\n"
            "/auth <password>: verify auth data\n"
            "/register: register for IP change notice\n"
            "/unregister: unregister for IP change notice\n"
            "/ip: show current IP address")
    await context.bot.send_message(chat_id=update.effective_chat.id, text=help)

async def check_event(context: ContextTypes.DEFAULT_TYPE):
    if len(LISTEN_IDS) == 0:
        return
    new_ip = await get_ip()
    last_ip = context.job.data.get("last_ip")
    if new_ip != last_ip:
        for chat_id in LISTEN_IDS:
            await context.bot.send_message(chat_id=chat_id, text=f'"NEW_IP": "{new_ip}"')
            # await context.bot.send_message(chat_id=chat_id, text=f'IP CHANGED: {last_ip} => {new_ip}')
        context.job.data["last_ip"] = new_ip

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("help", help))
    app.add_handler(CommandHandler('status', status))
    app.add_handler(CommandHandler('auth', auth))
    app.add_handler(CommandHandler('ip', ip))
    app.add_handler(CommandHandler('register', register))
    app.add_handler(CommandHandler('unregister', unregister))

    app.job_queue.run_repeating(
        check_event,
        interval=10,
        first=0,
        name="ip_watcher",
        data={"last_ip": None}
    )

    app.run_polling()
