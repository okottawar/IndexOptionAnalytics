import math
from dataclasses import dataclass
from typing import Literal, Tuple

OptionType = Literal["call", "put"]


# ============================================================
# Normal PDF / CDF
# ============================================================

def _norm_pdf(x: float) -> float:
    return (1.0 / math.sqrt(2 * math.pi)) * math.exp(-0.5 * x * x)


def _norm_cdf(x: float) -> float:
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


# ============================================================
# Black–Scholes Core
# ============================================================

@dataclass
class MarketParams:
    spot: float        # underlying price
    strike: float      # strike price
    maturity: float    # time to maturity (years)
    rate: float        # risk-free rate (annual, cont.)
    vol: float         # volatility (annualized)


def _d1_d2(mp: MarketParams) -> Tuple[float, float]:
    S, K, T, r, sigma = mp.spot, mp.strike, mp.maturity, mp.rate, mp.vol
    if T <= 0 or sigma <= 0 or S <= 0 or K <= 0:
        raise ValueError("S, K, T and vol must be positive.")
    d1 = (math.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * math.sqrt(T))
    d2 = d1 - sigma * math.sqrt(T)
    return d1, d2


def bs_price(mp: MarketParams, option_type: OptionType) -> float:
    d1, d2 = _d1_d2(mp)
    S, K, T, r = mp.spot, mp.strike, mp.maturity, mp.rate
    if option_type == "call":
        return S * _norm_cdf(d1) - K * math.exp(-r * T) * _norm_cdf(d2)
    elif option_type == "put":
        return K * math.exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)
    else:
        raise ValueError("option_type must be 'call' or 'put'")


# ============================================================
# Greeks
# ============================================================

@dataclass
class Greeks:
    delta: float
    gamma: float
    vega: float   # per 1% vol change
    theta: float  # per year
    rho: float    # per 1% rate change


def bs_greeks(mp: MarketParams, option_type: OptionType) -> Greeks:
    d1, d2 = _d1_d2(mp)
    S, K, T, r, sigma = mp.spot, mp.strike, mp.maturity, mp.rate, mp.vol
    pdf_d1 = _norm_pdf(d1)

    # Delta
    if option_type == "call":
        delta = _norm_cdf(d1)
    elif option_type == "put":
        delta = _norm_cdf(d1) - 1.0
    else:
        raise ValueError("option_type must be 'call' or 'put'")

    # Gamma (same for call & put)
    gamma = pdf_d1 / (S * sigma * math.sqrt(T))

    # Vega (per 1% change in vol)
    vega = S * pdf_d1 * math.sqrt(T) / 100.0

    # Theta (per year)
    first_term = - (S * pdf_d1 * sigma) / (2.0 * math.sqrt(T))
    if option_type == "call":
        theta = first_term - r * K * math.exp(-r * T) * _norm_cdf(d2)
        rho = K * T * math.exp(-r * T) * _norm_cdf(d2) / 100.0
    else:
        theta = first_term + r * K * math.exp(-r * T) * _norm_cdf(-d2)
        rho = -K * T * math.exp(-r * T) * _norm_cdf(-d2) / 100.0

    return Greeks(delta=delta, gamma=gamma, vega=vega, theta=theta, rho=rho)


# ============================================================
# Implied Volatility (Bisection)
# ============================================================

def implied_vol(
    market_price: float,
    mp: MarketParams,
    option_type: OptionType,
    vol_lower: float = 1e-4,
    vol_upper: float = 5.0,
    tol: float = 1e-6,
    max_iter: int = 100
) -> float:
    """
    Solve for implied volatility using the bisection method.
    Returns sigma such that BS price ~= market_price.
    """
    low, high = vol_lower, vol_upper

    for _ in range(max_iter):
        mid = 0.5 * (low + high)
        trial = MarketParams(
            spot=mp.spot,
            strike=mp.strike,
            maturity=mp.maturity,
            rate=mp.rate,
            vol=mid,
        )
        price_mid = bs_price(trial, option_type)
        diff = price_mid - market_price

        if abs(diff) < tol:
            return mid

        if diff > 0:
            high = mid
        else:
            low = mid

    return 0.5 * (low + high)
