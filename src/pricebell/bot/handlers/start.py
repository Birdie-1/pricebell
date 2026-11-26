from telegram import Update
from telegram.ext import ContextTypes

from pricebell.messages import pick_lang, t


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.effective_user is None or update.message is None:
        return

    user_lang = pick_lang(update.effective_user.language_code)

    reply = t("start.welcome", user_lang)

    await update.message.reply_text(reply)
