# app.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import math

st.set_page_config(page_title="Can I Afford This?", layout="centered")

st.title("💸 Can I Afford This? – Budgeting App")

# --- Input Fields ---
income = st.number_input("Monthly Income ($)", min_value=0.0, step=100.0)
expenses = st.number_input("Monthly Expenses ($)", min_value=0.0, step=100.0)
balance = st.number_input("Current Bank Balance ($)", min_value=0.0, step=100.0)
purchase = st.number_input("Purchase Amount ($)", min_value=0.0, step=50.0)

use_emi = st.checkbox("Buy in EMI?")

if use_emi:
    emi_months = st.number_input("EMI Duration (months)", min_value=1, step=1)
    interest_rate = st.number_input("Interest Rate (% per year)", min_value=0.0, step=0.5)

chart_type = st.selectbox("Choose Chart Type", ["Bar", "Pie"])

# --- Session State for History ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Calculate Button ---
if st.button("Can I Afford This?"):
    emi_amount = 0
    total_payable = purchase

    if use_emi:
        r = interest_rate / 12 / 100
        emi_amount = (purchase * r * math.pow(1 + r, emi_months)) / (math.pow(1 + r, emi_months) - 1)
        total_payable = emi_amount * emi_months

    monthly_outflow = emi_amount if use_emi else purchase
    leftover = income - expenses - monthly_outflow

    result = "✅ You can afford this!" if leftover >= 0 else "❌ Not affordable right now."
    st.markdown(f"### {result}")
    st.write(f"**After this purchase, your monthly leftover would be:** ${leftover:.2f}")

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.session_state.history.append({
        "Time": timestamp,
        "Result": result,
        "Leftover": round(leftover, 2),
        "Purchase": round(purchase, 2),
        "Monthly EMI": round(emi_amount, 2) if use_emi else 0
    })

    # --- Chart ---
    labels = ['Income', 'Expenses', 'Leftover', 'Purchase']
    values = [income, expenses, leftover, monthly_outflow]

    fig, ax = plt.subplots()
    if chart_type == "Bar":
        ax.bar(labels, values, color=["green", "red", "blue", "orange"])
    else:
        ax.pie(values, labels=labels, autopct='%1.1f%%', colors=["green", "red", "blue", "orange"])
        ax.axis("equal")
    st.pyplot(fig)

# --- History ---
st.subheader("History")
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button("📁 Download CSV", csv, "history.csv", "text/csv", key='download-csv')

    if st.button("🗑️ Clear History"):
        st.session_state.history = []
        st.experimental_rerun()
else:
    st.write("No history yet.")

