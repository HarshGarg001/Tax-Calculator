import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Income Tax Calculator", layout="wide")

# 🎨 Light/Dark Mode Toggle
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

st.markdown(
    f"""
    <style>
    body {{
        background-color: {"#0E1117" if st.session_state.theme=="dark" else "#F5F5F5"};
        color: {"white" if st.session_state.theme=="dark" else "black"};
    }}
    .stButton button {{
        background-color: {"#4CAF50" if st.session_state.theme=="light" else "#1DB954"};
        color: white;
        border-radius: 8px;
        padding: 8px 16px;
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("💰 Income Tax Calculator")
st.button("🌗 Toggle Theme", on_click=toggle_theme)

# 🏗 Layout - Two Columns
left, right = st.columns([1, 2])

with left:
    st.header("🔢 Enter Your Details")

    gross_salary = st.number_input("💼 Gross Salary Income (₹)", value=600000, step=1000)
    other_income = st.number_input("📄 Income from Other Sources (₹)", value=50000, step=1000)
    stcg = st.number_input("📈 Short Term Capital Gains (₹)", value=0, step=1000)
    ltcg = st.number_input("📊 Long Term Capital Gains (₹)", value=0, step=1000)
    crypto = st.number_input("🪙 Crypto Income (₹)", value=0, step=1000)
    lottery = st.number_input("🎟 Lottery Income (₹)", value=0, step=1000)

    regime = st.radio("Select Tax Regime", ["Old Regime", "New Regime"])

    deductions = st.number_input("Total Deductions (₹)", value=150000, step=1000)

# 💰 Tax Calculation Logic
def calculate_tax(income, regime):
    tax = 0
    slabs = []

    if regime == "Old Regime":
        slab_rates = [(250000, 0), (250000, 5), (500000, 20), (float("inf"), 30)]
    else:
        slab_rates = [(300000, 0), (300000, 5), (300000, 10), (300000, 15),
                      (300000, 20), (300000, 25), (float("inf"), 30)]

    remaining = income
    for slab, rate in slab_rates:
        taxable = min(remaining, slab)
        tax_amount = taxable * (rate/100)
        slabs.append({"Slab": f"{slab}", "Rate": f"{rate}%", "Taxable": taxable, "Tax": tax_amount})
        tax += tax_amount
        remaining -= taxable
        if remaining <= 0:
            break

    return tax, pd.DataFrame(slabs)

# Compute
gross_total = gross_salary + other_income
taxable_income = max(0, gross_total - deductions)

slab_tax, df_slab = calculate_tax(taxable_income, regime)
special_tax = stcg*0.15 + crypto*0.30 + lottery*0.30 + max(0, ltcg-100000)*0.10
total_tax = slab_tax + special_tax
cess = total_tax * 0.04
final_tax = total_tax + cess

with right:
    st.header("📊 Tax Calculation Summary")

    st.metric("Total Tax Payable", f"₹ {final_tax:,.0f}")

    st.subheader("🧾 Tax Distribution")
    fig = px.pie(
        names=["Tax from Slab Income", "Special Income Tax", "Cess"],
        values=[slab_tax, special_tax, cess],
        color_discrete_sequence=px.colors.qualitative.Set2
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("📈 Tax Breakdown (Slabs)")
    st.dataframe(df_slab)

    st.write(f"💡 **Gross Income:** ₹ {gross_total:,.0f}")
    st.write(f"💡 **Deductions:** ₹ {deductions:,.0f}")
    st.write(f"💡 **Taxable Income:** ₹ {taxable_income:,.0f}")
