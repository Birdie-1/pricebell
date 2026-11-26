from telegram.ext import Application, CommandHandler

from pricebell.bot.handlers.start import start


def build_application(token: str) -> Application:
    # building application
    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    return app
