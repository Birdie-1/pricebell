import pytest

from pricebell.messages import pick_lang, t


def test_pick_lang_en() -> None:
    assert pick_lang("en") == "en"


def test_pick_lang_en_us() -> None:
    assert pick_lang("en-US") == "en"


def test_pick_lang_th() -> None:
    assert pick_lang("th") == "th"


def test_pick_lang_none() -> None:
    assert pick_lang(None) == "th"


def test_pick_lang_ja() -> None:
    assert pick_lang("ja") == "th"


def test_t_returns_english_text() -> None:
    assert "PriceBell" in t("start.welcome", "en")


def test_t_unknown_key_raises() -> None:
    with pytest.raises(KeyError):
        t("no.such.key", "th")
