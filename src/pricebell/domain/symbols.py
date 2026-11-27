import re
from typing import Final

# Thai tickers that get ".BK" appended. SET50 constituents for H1 2026
# (SET document dated 15 Dec 2025) plus BCP, which joined for H2 2026.
# The full H2 2026 list was not available; extra tickers are harmless here.
THAI_STOCKS: Final[frozenset[str]] = frozenset(
    {
        "ADVANC",
        "AOT",
        "AWC",
        "BANPU",
        "BBL",
        "BCP",
        "BDMS",
        "BEM",
        "BH",
        "BJC",
        "BTS",
        "CBG",
        "CCET",
        "CENTEL",
        "COM7",
        "CPALL",
        "CPF",
        "CPN",
        "CRC",
        "DELTA",
        "EGCO",
        "GPSC",
        "GULF",
        "HMPRO",
        "IVL",
        "KBANK",
        "KKP",
        "KTB",
        "KTC",
        "LH",
        "MINT",
        "MTC",
        "OR",
        "OSP",
        "PTT",
        "PTTEP",
        "PTTGC",
        "RATCH",
        "SAWAD",
        "SCB",
        "SCC",
        "SCGP",
        "TCAP",
        "TIDLOR",
        "TISCO",
        "TLI",
        "TOP",
        "TRUE",
        "TTB",
        "TU",
        "WHA",
    }
)

# Thai names for non-stock assets, mapped straight to their Yahoo symbol.
NICKNAMES: Final[dict[str, str]] = {
    "ทอง": "GC=F",
    "น้ำมัน": "CL=F",
    "เบรนท์": "BZ=F",
    "ดอลลาร์": "THB=X",
}

# Characters Yahoo uses in symbols (e.g. "PTT.BK", "GC=F", "^SET50.BK", "BRK-B").
SYMBOL_PATTERN: Final[re.Pattern[str]] = re.compile(r"[A-Z0-9.=^-]{1,15}")


class InvalidSymbolError(ValueError):
    """The input cannot be a symbol: it is empty or has characters Yahoo never uses.

    This is a format check only. Whether the symbol exists is the provider's job.
    """


def normalise(raw: str) -> str:
    """Turn user input into a Yahoo symbol.

    Raises:
        InvalidSymbolError: if the input is not a nickname and not a valid symbol.
    """
    upper = raw.upper().strip()
    if upper in NICKNAMES:
        return NICKNAMES[upper]
    if not SYMBOL_PATTERN.fullmatch(upper):
        raise InvalidSymbolError(raw)
    if upper in THAI_STOCKS:
        return f"{upper}.BK"
    return upper
