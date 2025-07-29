import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Income Tax Calculator", layout="wide")

# ---- THEME STATE ----
if "theme" not in st.session_state:
    st.session_state.theme = "light"

# ---- THEME TOGGLE (REAL) ----
colA, colB = st.columns([10, 1])
with colB:
    toggle = st.toggle("🌙", value=(st.session_state.theme=="dark"), label_visibility="collapsed")
    st.session_state.theme = "dark" if toggle else "light"

# ---- TAX SLABS ----
old_slabs = [
    (0, 250000, 0.0),
    (250000, 500000, 0.05),
    (500000, 1000000, 0.2),
    (1000000, float("inf"), 0.3),
]

new_slabs = [
    (0, 300000, 0.0),
    (300000, 600000, 0.05),
    (600000, 900000, 0.1),
    (900000, 1200000, 0.15),
    (1200000, 1500000, 0.2),
    (1500000, float("inf"), 0.3),
]

# ---- TAX CALCULATION FUNCTION ----
def slab_tax(income, slabs):
    tax = 0
    breakdown = []
    for lower, upper, rate in slabs:
        if income > lower:
            taxable_amt = min(income, upper) - lower
            tax_amt = taxable_amt * rate
            breakdown.append((f"₹{lower:,} – ₹{upper if upper!=float('inf') else '∞'}", f"{rate*100:.0f}%", taxable_amt, tax_amt))
            tax += tax_amt
    return tax, breakdown

def total_tax(salary, other_income, deductions, special_income, slabs):
    gross_income = salary + other_income
    taxable_income = max(0, gross_income - deductions)
    slab_tax_amt, breakdown = slab_tax(taxable_income, slabs)

    special_tax = (
        special_income["STCG"] * 0.15 +
        max(0, special_income["LTCG"] - 100000) * 0.10 +
        special_income["Lottery"] * 0.30 +
        special_income["Crypto"] * 0.30
    )

    total = slab_tax_amt + special_tax
    cess = total * 0.04
    return total + cess, breakdown, slab_tax_amt, special_tax, cess

# ---- INPUT PANEL ----
with st.sidebar:
    st.markdown("### 📋 Enter Your Details")
    salary = st.number_input("Salary Income (₹)", 0, step=5000)
    other_income = st.number_input("Other Income (₹)", 0, step=5000)

    st.markdown("### 💰 Special Income")
    STCG = st.number_input("STCG (15%)", 0, step=5000)
    LTCG = st.number_input("LTCG (>₹1L @10%)", 0, step=5000)
    Lottery = st.number_input("Lottery (30%+Cess)", 0, step=5000)
    Crypto = st.number_input("Crypto Income (30%+Cess)", 0, step=5000)

    st.markdown("### 📉 Deductions (Old Regime)")
    d80C = st.number_input("80C", 0, step=5000)
    d80D = st.number_input("80D", 0, step=5000)
    hra = st.number_input("HRA Exemption", 0, step=5000)

deductions_old = 50000 + d80C + d80D + hra
deductions_new = 50000

special_income = {"STCG": STCG, "LTCG": LTCG, "Lottery": Lottery, "Crypto": Crypto}

# ---- CALCULATE TAXES ----
tax_old, breakdown_old, slab_old, special_old, cess_old = total_tax(
    salary, other_income, deductions_old, special_income, old_slabs
)
tax_new, breakdown_new, slab_new, special_new, cess_new = total_tax(
    salary, other_income, deductions_new, special_income, new_slabs
)

savings = tax_old - tax_new
better = "✅ New Regime is Better" if savings > 0 else "✅ Old Regime is Better"

# ---- COMPARISON TABLE ----
df = pd.DataFrame({
    "Particulars": ["Gross Income", "Total Deductions", "Taxable Income", "Tax from Slab", "Tax from Special", "Cess (4%)", "Total Tax Payable"],
    "Old Regime": [f"₹{salary+other_income:,}", f"₹{deductions_old:,}", f"₹{salary+other_income-deductions_old:,}", f"₹{slab_old:,}", f"₹{special_old:,}", f"₹{cess_old:,.0f}", f"₹{tax_old:,.0f}"],
    "New Regime": [f"₹{salary+other_income:,}", f"₹{deductions_new:,}", f"₹{salary+other_income-deductions_new:,}", f"₹{slab_new:,}", f"₹{special_new:,}", f"₹{cess_new:,.0f}", f"₹{tax_new:,.0f}"]
})

col1, col2 = st.columns([2, 3])
with col1:
    st.subheader("📊 Tax Comparison Table")
    st.dataframe(df, use_container_width=True)
    st.success(f"💡 {better} – You Save ₹{abs(savings):,.0f}")

with col2:
    fig = px.bar(
        x=["Old Regime", "New Regime"],
        y=[tax_old, tax_new],
        labels={"x": "Regime", "y": "Total Tax (₹)"},
        color=["Old Regime", "New Regime"],
        color_discrete_map={"Old Regime": "#ff6b6b", "New Regime": "#1dd1a1"},
        text=[f"₹{tax_old:,.0f}", f"₹{tax_new:,.0f}"]
    )
    fig.update_traces(textposition="outside")
    st.plotly_chart(fig, use_container_width=True)

col3, col4 = st.columns(2)
with col3:
    st.subheader("📄 Old Regime Slab Calculation")
    st.dataframe(pd.DataFrame(breakdown_old, columns=["Slab", "Rate", "Taxable Income", "Tax"]), use_container_width=True)

with col4:
    st.subheader("📄 New Regime Slab Calculation")
    st.dataframe(pd.DataFrame(breakdown_new, columns=["Slab", "Rate", "Taxable Income", "Tax"]), use_container_width=True)
