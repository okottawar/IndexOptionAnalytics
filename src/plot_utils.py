import matplotlib.pyplot as plt
import pandas as pd


def plot_iv_smile(df: pd.DataFrame, option_type: str):
    """
    Create and return a matplotlib Figure showing the IV smile for calls or puts.
    """
    subset = df[df["type"] == option_type].sort_values("strike")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(subset["strike"], subset["iv"], marker="o")
    ax.set_title(f"IV Smile - {option_type.upper()}")
    ax.set_xlabel("Strike")
    ax.set_ylabel("Implied Volatility")
    ax.grid(True)
    return fig


def clean_iv(df: pd.DataFrame, min_iv: float = 0.01, max_iv: float = 3.0) -> pd.DataFrame:
    """
    Filter out unrealistic IVs.
    """
    return df[(df["iv"] > min_iv) & (df["iv"] < max_iv)].copy()


def find_atm_strike(df: pd.DataFrame) -> float:
    """
    Find the strike closest to the spot price (ATM).
    """
    if df.empty:
        return float("nan")
    spot = df["spot"].iloc[0]
    atm_row = df.iloc[(df["strike"] - spot).abs().argmin()]
    return atm_row["strike"]
