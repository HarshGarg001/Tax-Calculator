import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Income Tax Calculator", page_icon="💰", layout="wide")

# =========================
# 🌗 Theme Toggle (Working)
# =========================
if "theme" not in st.session_state:
    st.session_state.theme = "light"

def toggle_theme():
    st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"

col1, col2 = st.columns([10, 1])
with col2:
    if st.button("🌞" if st.session_state.theme == "light" else "🌙"):
        toggle_theme()

# Apply custom theme CSS dynamically
bg_color = "#FFFFFF" if st.session_state.theme == "light" else "#0E1117"
text_color = "#000000" if st.session_state.theme == "light" else "#FFFFFF"

st.markdown(
    f"""
    <style>
        .stApp {{
            background-color: {bg_color};
            color: {text_color};
        }}
    </style>
    """,
    unsafe_allow_html=True
)

# Plotly theme
plotly_theme = "plotly_white" if st.session_state.theme == "light" else "plotly_dark"

# =========================
# Inputs (Sidebar for Desktop, Top for Mobile)
# =========================
params = st.query_params
is_mobile = params.get("isMobile", "false") == "true"

if is_mobile:
    st.subheader("🔢 Enter Your Details")
    salary_income = st.number_input("Salary Income (₹)", 0, step=10000)
    other_income = st.number_input("Other Income (₹)", 0, step=5000)
    stcg = st.number_input("STCG (15%)", 0, step=1000)
    ltcg = st.number_input("LTCG (>₹1L @10%)", 0, step=1000)
    lottery = st.number_input("Lottery (30%+Cess)", 0, step=1000)
    crypto = st.number_input("Crypto Income (30%+Cess)", 0, step=1000)
    st.subheader("Deductions (Old Regime)")
    ded_80c = st.number_input("80C", 0, 150000, step=5000)
    ded_80d = st.number_input("80D", 0, step=5000)
    ded_hra = st.number_input("HRA Exemption", 0, step=5000)
    ded_80tta = st.number_input("80TTA/80TTB", 0, step=5000)
else:
    with st.sidebar:
        st.header("🔢 Enter Your Details")
        salary_income = st.number_input("Salary Income (₹)", 0, step=10000)
        other_income = st.number_input("Other Income (₹)", 0, step=5000)

        st.subheader("Special Income")
        stcg = st.number_input("STCG (15%)", 0, step=1000)
        ltcg = st.number_input("LTCG (>₹1L @10%)", 0, step=1000)
        lottery = st.number_input("Lottery (30%+Cess)", 0, step=1000)
        crypto = st.number_input("Crypto Income (30%+Cess)", 0, step=1000)

        st.subheader("Deductions (Old Regime)")
        ded_80c = st.number_input("80C", 0, 150000, step=5000)
        ded_80d = st.number_input("80D", 0, step=5000)
        ded_hra = st.number_input("HRA Exemption", 0, step=5000)
        ded_80tta = st.number_input("80TTA/80TTB", 0, step=5000)

# =========================
# Tax Calculation
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

# Income & deductions
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
# Savings Highlight
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
                 color_discrete_map={"Old Regime":"#EF553B","New Regime":"#00CC96"},
                 template=plotly_theme)
    st.plotly_chart(fig, use_container_width=True)

with col2:
    pie_old = pd.DataFrame({"Type":["Slab Tax","Special Tax","Cess"],
                            "Value":[old_tax_slab, special_tax, (old_tax_slab+special_tax)*0.04]})
    pie_new = pd.DataFrame({"Type":["Slab Tax","Special Tax","Cess"],
                            "Value":[new_tax_slab, special_tax, (new_tax_slab+special_tax)*0.04]})

    st.plotly_chart(px.pie(pie_old, names="Type", values="Value", title="Old Regime Tax Distribution", template=plotly_theme), use_container_width=True)
    st.plotly_chart(px.pie(pie_new, names="Type", values="Value", title="New Regime Tax Distribution", template=plotly_theme), use_container_width=True)

st.caption("Built with ❤️ using Streamlit")
