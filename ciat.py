import streamlit as st
import pandas as pd
import math
import matplotlib.pyplot as plt
from io import StringIO

st.set_page_config(page_title="Can I Afford This?", layout="centered")

st.title("💸 Can I Afford This?")
st.markdown("A real-time lifestyle budgeting tool to help you make smarter purchase decisions.")

# -------------------
# Sidebar - Input
# -------------------
st.sidebar.header("User Inputs")

income = st.sidebar.number_input("Monthly Income ($)", min_value=0.0, value=3000.0)
expenses = st.sidebar.number_input("Monthly Expenses ($)", min_value=0.0, value=2000.0)
bank_balance = st.sidebar.number_input("Current Bank Balance ($)", min_value=0.0, value=500.0)
purchase = st.sidebar.number_input("Purchase Amount ($)", min_value=0.0, value=120.0)

buy_emi = st.sidebar.checkbox("Buy in EMI?")
emi_months = st.sidebar.number_input("EMI Duration (months)", min_value=1, value=6)
interest_rate = st.sidebar.number_input("Interest Rate (% per year)", min_value=0.0, value=0.0)

chart_type = st.sidebar.selectbox("Choose Chart Type", ["Pie", "None"])

# -------------------
# Logic
# -------------------
result = ""
leftover = 0
emi_amount = 0
history = []

if st.button("Can I Afford This?"):
    monthly_leftover = income - expenses
    r = (interest_rate / 100) / 12  # monthly interest rate

    if buy_emi:
        if r == 0:
            emi_amount = purchase / emi_months
        else:
            try:
                emi_amount = (purchase * r * math.pow(1 + r, emi_months)) / (math.pow(1 + r, emi_months) - 1)
            except ZeroDivisionError:
                emi_amount = purchase / emi_months  # fallback
        affordable = monthly_leftover - emi_amount >= 0
        result = f"Your monthly EMI would be **${emi_amount:.2f}**"
        leftover = monthly_leftover - emi_amount
    else:
        affordable = (monthly_leftover >= purchase) or (bank_balance >= purchase)
        result = f"You are paying the full amount of **${purchase:.2f}**"
        leftover = monthly_leftover - purchase

    if affordable:
        st.success("✅ You can afford this!")
    else:
        st.error("❌ You cannot afford this right now.")
    
    st.markdown(f"### Result\n{result}")
    st.markdown(f"**Monthly Leftover After Purchase:** ${leftover:.2f}")
    
    # Append to session history
    if "history" not in st.session_state:
        st.session_state.history = []
    st.session_state.history.append({
        "Income": income,
        "Expenses": expenses,
        "Purchase": purchase,
        "Bank Balance": bank_balance,
        "EMI": buy_emi,
        "EMI Amount": round(emi_amount, 2) if buy_emi else 0,
        "Leftover": round(leftover, 2),
        "Interest %": interest_rate
    })

# -------------------
# Show History
# -------------------
st.markdown("---")
st.markdown("### 🧾 History")

if "history" in st.session_state and st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    st.dataframe(df)

    if st.button("Clear History"):
        st.session_state.history = []

    # CSV Download
    csv = df.to_csv(index=False)
    st.download_button("📥 Download CSV", data=csv, file_name="budget_history.csv", mime="text/csv")

# -------------------
# Pie Chart
# -------------------
if chart_type == "Pie" and "history" in st.session_state and st.session_state.history:
    latest = st.session_state.history[-1]
    labels = ["Expenses", "Leftover", "EMI" if latest["EMI"] else "Purchase"]
    sizes = [latest["Expenses"], latest["Leftover"], latest["EMI Amount"] if latest["EMI"] else latest["Purchase"]]
    colors = ["#FF9999", "#99FF99", "#9999FF"]

    fig, ax = plt.subplots()
    ax.pie(sizes, labels=labels, colors=colors, autopct="%1.1f%%", startangle=90)
    ax.axis("equal")
    st.pyplot(fig)
