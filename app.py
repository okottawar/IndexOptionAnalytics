import streamlit as st
import pandas as pd
from datetime import date
from pathlib import Path

from src.option_chain_loader import load_option_chain_from_csv
from src.analyze_option_chain import analyze_option_chain
from src.plot_utils import plot_iv_smile, clean_iv

st.set_page_config(page_title="Index Options Analytics", layout="wide")

st.title("Index Options Analytics – Implied Volatility & Greeks")

st.markdown(
    """
Upload an NSE option-chain CSV, configure the underlying parameters,
and analyze **implied volatility smiles** and **Greeks** for NIFTY / BANKNIFTY options.
"""
)

# Sidebar
st.sidebar.header("Inputs")

underlying_name = st.sidebar.selectbox("Underlying", ["NIFTY", "BANKNIFTY"])
spot_price = st.sidebar.number_input(
    "Spot price", min_value=1000.0, value=24200.0, step=50.0
)
risk_free_rate_pct = st.sidebar.number_input(
    "Risk-free rate (annual, %)", min_value=0.0, value=6.0, step=0.25
)
risk_free_rate = risk_free_rate_pct / 100.0
expiry = st.sidebar.date_input("Expiry date", value=date(2025, 12, 9))

uploaded_file = st.file_uploader("Upload NSE option-chain CSV", type=["csv"])

run_btn = st.button("Run analysis")

if run_btn and uploaded_file is not None:
    with st.spinner("Loading and analyzing option chain..."):
        raw_df = pd.read_csv(uploaded_file)

        data_dir = Path("data")
        data_dir.mkdir(exist_ok=True)
        tmp_path = data_dir / "_uploaded_tmp.csv"
        raw_df.to_csv(tmp_path, index=False)

        quotes = load_option_chain_from_csv(
            csv_path=tmp_path,
            spot_price=spot_price,
            expiry=expiry,
            risk_free_rate=risk_free_rate,
            symbol=underlying_name,
        )

        if not quotes:
            st.error("No valid options found in the CSV.")
        else:
            df = analyze_option_chain(quotes)
            df_clean = clean_iv(df)

            st.subheader(f"Summary for {underlying_name}")
            st.dataframe(df_clean.head(20))

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("IV Smile – Calls")
                fig_call = plot_iv_smile(df_clean, option_type="call")
                st.pyplot(fig_call)

            with col2:
                st.subheader("IV Smile – Puts")
                fig_put = plot_iv_smile(df_clean, option_type="put")
                st.pyplot(fig_put)

elif run_btn and uploaded_file is None:
    st.warning("Please upload a CSV file first.")
