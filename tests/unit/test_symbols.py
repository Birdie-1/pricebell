import pytest

from pricebell.domain.symbols import InvalidSymbolError, normalise


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("ptt", "PTT.BK"),
        ("nvda", "NVDA"),
        ("  PTT  ", "PTT.BK"),
        ("PTT.BK", "PTT.BK"),
        ("GC=F", "GC=F"),
        ("bh", "BH.BK"),
        ("ทอง", "GC=F"),
        ("น้ำมัน", "CL=F"),
        ("เบรนท์", "BZ=F"),
        (" ดอลลาร์ ", "THB=X"),
    ],
)
def test_normalise_valid_input(raw: str, expected: str) -> None:
    assert normalise(raw) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "   ", "hello world", "PTT!", "<script>", "สวัสดี", "A" * 16],
)
def test_normalise_invalid_input_raises(raw: str) -> None:
    with pytest.raises(InvalidSymbolError):
        normalise(raw)
