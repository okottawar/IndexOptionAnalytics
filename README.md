# Index Options Analytics – Implied Volatility & Greeks 

This project implements a full **index options analytics engine** for NIFTY / BANKNIFTY using:

- **Black–Scholes European option pricing**
- **Full Greeks (Δ, Γ, Vega, Θ, ρ)**
- **Implied Volatility extraction** using a numerical bisection solver
- **Real NSE option-chain CSV ingestion**
- **Interactive Streamlit dashboard**
- **Visualization of IV smile curves** for calls and puts

The goal is to demonstrate practical derivatives modelling, numerical methods, and real-market data analysis in a clean, modular way.

---

## 🚀 Features

### Black–Scholes Pricing Engine  
Compute European call/put prices with adjustable spot, strike, maturity, rate, and volatility.

### Greeks Computation  
For each option:  
- **Delta** (rate of price change w.r.t underlying)  
- **Gamma** (curvature)  
- **Vega** (sensitivity to volatility)  
- **Theta** (time decay)  
- **Rho** (interest rate sensitivity)

### Implied Volatility Solver  
Automatically computes implied volatility from market LTP using a stable **bisection method**.

### Real Option Chain Integration  
Upload NSE option-chain CSVs and convert them into structured option objects.  
Handles:  
- Number formatting (e.g., `"24,300.00"`)  
- Missing values  
- Calls + Puts jointly

### IV Smile Visualization  
Generate implied volatility smiles across strikes for calls and puts.

###  Streamlit Web App  
User-friendly interface:

- Upload CSV  
- Configure spot, expiry, risk-free rate  
- Run analysis  
- View IV smiles and Greeks tables  
- No coding required

---

## 🧩 Data Source

**NSE INDIA OPTION CHAIN** - https://www.nseindia.com/option-chain
