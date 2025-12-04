import pandas as pd
from dataclasses import dataclass
from datetime import date
from typing import List, Literal

OptionType = Literal["call", "put"]


@dataclass
class OptionQuote:
    symbol: str
    spot: float
    strike: float
    expiry: date
    option_type: OptionType
    ltp: float
    risk_free_rate: float
    time_to_maturity: float


def clean_num(x):
    """
    Convert values like '23,750.00' or '-' into floats.
    Returns None if not parseable.
    """
    if pd.isna(x):
        return None
    x = str(x).replace(",", "").strip()
    if x in ["", "-", "—"]:
        return None
    try:
        return float(x)
    except ValueError:
        return None


def load_option_chain_from_csv(
    csv_path,
    spot_price: float,
    expiry: date,
    risk_free_rate: float = 0.06,
    symbol: str = "NIFTY",
) -> List[OptionQuote]:
    """
    Load an NSE-style option chain CSV into a list of OptionQuote.

    Expected column order after renaming:
    CALLS: OI, CHNG IN OI, VOLUME, IV, LTP, CHNG, BID QTY, BID, ASK, ASK QTY,
    STRIKE,
    PUTS: BID QTY, BID, ASK, ASK QTY, CHNG, LTP, IV, VOLUME, CHNG IN OI, OI
    """

    cols = [
        "calls_oi", "calls_chng_oi", "calls_volume", "calls_iv", "calls_ltp",
        "calls_chng", "calls_bid_qty", "calls_bid", "calls_ask", "calls_ask_qty",
        "strike",
        "puts_bid_qty", "puts_bid", "puts_ask", "puts_ask_qty",
        "puts_chng", "puts_ltp", "puts_iv", "puts_volume", "puts_chng_oi", "puts_oi"
    ]

    df = pd.read_csv(csv_path)

    # Force simpler column names
    df.columns = cols[:len(df.columns)]

    # Drop rows without a valid strike
    df = df[df["strike"].notna()].copy()

    # Time to maturity in years
    today = date.today()
    days_to_expiry = max((expiry - today).days, 0)
    ttm = days_to_expiry / 365.0

    quotes: List[OptionQuote] = []

    for _, r in df.iterrows():
        strike = clean_num(r["strike"])
        if strike is None:
            continue

        calls_ltp = clean_num(r.get("calls_ltp"))
        puts_ltp = clean_num(r.get("puts_ltp"))

        # CALL
        if calls_ltp is not None and calls_ltp > 0:
            quotes.append(
                OptionQuote(
                    symbol=symbol,
                    spot=spot_price,
                    strike=strike,
                    expiry=expiry,
                    option_type="call",
                    ltp=calls_ltp,
                    risk_free_rate=risk_free_rate,
                    time_to_maturity=ttm,
                )
            )

        # PUT
        if puts_ltp is not None and puts_ltp > 0:
            quotes.append(
                OptionQuote(
                    symbol=symbol,
                    spot=spot_price,
                    strike=strike,
                    expiry=expiry,
                    option_type="put",
                    ltp=puts_ltp,
                    risk_free_rate=risk_free_rate,
                    time_to_maturity=ttm,
                )
            )

    return quotes
