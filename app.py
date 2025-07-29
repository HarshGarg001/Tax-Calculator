import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Income Tax Calculator", page_icon="💰", layout="wide")

# =========================
# 🌗 Theme Toggle
# =========================
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

def toggle_theme():
    st.session_state.dark_mode = not st.session_state.dark_mode

st.markdown("""
    <style>
    .theme-toggle {
        position: fixed;
        top: 15px;
        right: 20px;
        background: #eee;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: bold;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 8px;
    }
    </style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([10, 1])
with col2:
    if st.button("🌞" if not st.session_state.dark_mode else "🌙"):
        toggle_theme()

# =========================
# 📱 Responsive Layout
# =========================
is_mobile = st.experimental_get_query_params().get("isMobile", ["false"])[0] == "true"

if is_mobile:
    st.title("💰 Income Tax Calculator")
    st.subheader("Enter Your Details")
else:
    st.title("💰 Income Tax Calculator")

# Inputs Section
if is_mobile:
    income_col = st.container()
else:
    with st.sidebar:
        st.header("🔢 Enter Your Details")

# Inputs
salary_income = st.sidebar.number_input("Salary Income (₹)", 0, step=10000)
other_income = st.sidebar.number_input("Other Income (₹)", 0, step=5000)

st.sidebar.subheader("Special Income")
stcg = st.sidebar.number_input("STCG (15%)", 0, step=1000)
ltcg = st.sidebar.number_input("LTCG (>₹1L @10%)", 0, step=1000)
lottery = st.sidebar.number_input("Lottery (30%+Cess)", 0, step=1000)
crypto = st.sidebar.number_input("Crypto Income (30%+Cess)", 0, step=1000)

st.sidebar.subheader("Deductions (Old Regime)")
ded_80c = st.sidebar.number_input("80C", 0, 150000, step=5000)
ded_80d = st.sidebar.number_input("80D", 0, step=5000)
ded_hra = st.sidebar.number_input("HRA Exemption", 0, step=5000)
ded_80tta = st.sidebar.number_input("80TTA/80TTB", 0, step=5000)

# =========================
# Tax Calculation Functions
# =========================
def calculate_slab_tax(taxable, regime):
    tax = 0
    if regime == "new":
        slabs = [(0,300000,0.0),(300000,600000,0.05),(600000,900000,0.10),
                 (900000,1200000,0.15),(1200000,1500000,0.20),(1500000,float('inf'),0.30)]
    else:
        slabs = [(0,250000,0.0),(250000,500000,0.05),(500000,1000000,0.20),(1000000,float('inf'),0.30)]
    for lower, upper, rate in slabs:
        if taxable > lower:
            portion = min(taxable, upper) - lower
            tax += portion * rate
    return tax

# Inputs for both regimes
gross_income = salary_income + other_income + stcg + ltcg + lottery + crypto
standard_deduction = 50000

old_deductions = min(ded_80c, 150000) + ded_80d + ded_hra + ded_80tta + standard_deduction
old_taxable = salary_income + other_income - old_deductions
new_taxable = salary_income + other_income - standard_deduction

old_tax_slab = calculate_slab_tax(max(old_taxable,0), "old")
new_tax_slab = calculate_slab_tax(max(new_taxable,0), "new")

special_tax = stcg*0.15 + max((ltcg-100000),0)*0.10 + (lottery+crypto)*0.30

old_total = (old_tax_slab + special_tax) * 1.04
new_total = (new_tax_slab + special_tax) * 1.04

# =========================
# Comparison Table
# =========================
data = {
    "Particulars": ["Gross Income","Total Deductions","Taxable Income","Tax from Slab","Tax from Special Income","Cess (4%)","Total Tax Payable"],
    "Old Regime": [gross_income, old_deductions, old_taxable, old_tax_slab, special_tax, (old_tax_slab+special_tax)*0.04, old_total],
    "New Regime": [gross_income, standard_deduction, new_taxable, new_tax_slab, special_tax, (new_tax_slab+special_tax)*0.04, new_total]
}

df = pd.DataFrame(data)

st.subheader("📊 Tax Comparison Table")
st.table(df.style.format({"Old Regime":"₹{:,.0f}","New Regime":"₹{:,.0f}"}))

# =========================
# Savings & Best Regime
# =========================
savings = old_total - new_total
if savings > 0:
    best_text = f"✅ New Regime is Better – You Save ₹{abs(savings):,.0f}"
else:
    best_text = f"✅ Old Regime is Better – You Save ₹{abs(savings):,.0f}"

st.success(best_text)

# =========================
# Charts
# =========================
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(x=["Old Regime","New Regime"], y=[old_total,new_total],
                 text=[f"₹{old_total:,.0f}",f"₹{new_total:,.0f}"],
                 color=["Old Regime","New Regime"],
                 title="Total Tax Payable",
                 color_discrete_map={"Old Regime":"red","New Regime":"green"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    pie_old = pd.DataFrame({"Type":["Slab Tax","Special Tax","Cess"],
                            "Value":[old_tax_slab, special_tax, (old_tax_slab+special_tax)*0.04]})
    pie_new = pd.DataFrame({"Type":["Slab Tax","Special Tax","Cess"],
                            "Value":[new_tax_slab, special_tax, (new_tax_slab+special_tax)*0.04]})

    st.plotly_chart(px.pie(pie_old, names="Type", values="Value", title="Old Regime Tax Distribution"), use_container_width=True)
    st.plotly_chart(px.pie(pie_new, names="Type", values="Value", title="New Regime Tax Distribution"), use_container_width=True)

st.caption("Built with ❤️ using Streamlit")
