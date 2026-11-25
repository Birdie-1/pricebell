import pytest
from pydantic import ValidationError

from pricebell.settings import Settings


def test_reads_token_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "test-token")

    settings = Settings(_env_file=None)

    assert settings.telegram_bot_token.get_secret_value() == "test-token"


def test_missing_token_raises(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("TELEGRAM_BOT_TOKEN", raising=False)

    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_token_not_shown_in_repr(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("TELEGRAM_BOT_TOKEN", "super-secret-token")

    settings = Settings(_env_file=None)

    assert "super-secret-token" not in repr(settings)
