import logging
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from pricebell.bot.app import build_application
from pricebell.settings import Settings

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    settings = Settings()
    bot_app = build_application(settings.telegram_bot_token.get_secret_value())
    await bot_app.initialize()
    await bot_app.updater.start_polling()
    await bot_app.start()
    logger.info("Bot Started")
    yield
    await bot_app.updater.stop()
    await bot_app.stop()
    await bot_app.shutdown()
    logger.info("Bot Stopped")


def create_app() -> FastAPI:
    logging.basicConfig(
        level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s"
    )
    logging.getLogger("httpx").setLevel(logging.WARNING)
    app = FastAPI(lifespan=lifespan)

    # anyone access /health url, this function will be called
    @app.get("/health")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    return app
