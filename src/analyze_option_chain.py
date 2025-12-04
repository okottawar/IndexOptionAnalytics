import pandas as pd
from typing import List

from .options_engine import MarketParams, bs_greeks, implied_vol
from .option_chain_loader import OptionQuote


def analyze_option_chain(quotes: List[OptionQuote]) -> pd.DataFrame:
    """
    For each option quote, compute implied volatility and Greeks.
    Returns a pandas DataFrame with all results.
    """
    records = []

    for q in quotes:
        base_params = MarketParams(
            spot=q.spot,
            strike=q.strike,
            maturity=q.time_to_maturity,
            rate=q.risk_free_rate,
            vol=0.2,  # initial guess used only for IV/Gamma denom check
        )

        iv = implied_vol(q.ltp, base_params, q.option_type)

        params_iv = MarketParams(
            spot=q.spot,
            strike=q.strike,
            maturity=q.time_to_maturity,
            rate=q.risk_free_rate,
            vol=iv,
        )

        g = bs_greeks(params_iv, q.option_type)

        records.append(
            {
                "symbol": q.symbol,
                "type": q.option_type,
                "strike": q.strike,
                "expiry": q.expiry,
                "spot": q.spot,
                "ltp": q.ltp,
                "iv": iv,
                "delta": g.delta,
                "gamma": g.gamma,
                "vega": g.vega,
                "theta": g.theta,
                "rho": g.rho,
            }
        )

    return pd.DataFrame(records)
