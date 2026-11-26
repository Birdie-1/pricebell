from typing import Literal

Lang = Literal["th", "en"]
DEFAULT_LANG: Lang = "th"

_MESSAGES: dict[str, dict[Lang, str]] = {
    "start.welcome": {
        "th": "สวัสดี ฉันคือ PriceBell เป็นบอทที่คอยเฝ้าราคาหุ้น ทอง น้ำมัน แล้วแจ้งเตือนเมื่อถึงเป้า",
        "en": (
            "Hi, I'm PriceBell. I watch stock, gold and oil prices and alert you "
            "when they hit your target."
        ),
    },
}


def pick_lang(language_code: str | None) -> Lang:
    if language_code is None:
        return DEFAULT_LANG
    if language_code.startswith("en"):
        return "en"
    return DEFAULT_LANG


def t(key: str, lang: Lang) -> str:
    return _MESSAGES[key][lang]
