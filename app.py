import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Income Tax Calculator", page_icon="💰", layout="wide")

st.title("💰 Income Tax Calculator (India)")
st.write("Compare Old vs New Regime and find which saves you more tax!")

# Sidebar Inputs
st.sidebar.header("📝 Enter Your Details")
name = st.sidebar.text_input("Name", "")
age_category = st.sidebar.selectbox("Age Category", ["<60", "60-80", ">80"])

salary_income = st.sidebar.number_input("Salary Income (₹)", 0, step=10000)
other_income = st.sidebar.number_input("Other Income (₹)", 0, step=5000)

st.sidebar.markdown("### Special Income")
stcg = st.sidebar.number_input("STCG (15%)", 0, step=1000)
ltcg = st.sidebar.number_input("LTCG (>₹1L @10%)", 0, step=1000)
lottery = st.sidebar.number_input("Lottery Winnings (30%+Cess)", 0, step=1000)
crypto = st.sidebar.number_input("Crypto Income (30%+Cess)", 0, step=1000)

# Deductions
st.sidebar.markdown("### Deductions (Applicable only for Old Regime)")
ded_80c = st.sidebar.number_input("80C", 0, 150000, step=5000)
ded_80d = st.sidebar.number_input("80D", 0, step=5000)
ded_hra = st.sidebar.number_input("HRA Exemption", 0, step=5000)
ded_80tta = st.sidebar.number_input("80TTA/80TTB", 0, step=5000)

# Functions for tax slabs
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

# Calculation logic
gross_income = salary_income + other_income + stcg + ltcg + lottery + crypto
standard_deduction = 50000
old_deductions = min(ded_80c, 150000) + ded_80d + ded_hra + ded_80tta + standard_deduction

# Taxable incomes
old_taxable = salary_income + other_income - old_deductions
new_taxable = salary_income + other_income - standard_deduction

# Slab tax
old_tax_slab = calculate_slab_tax(max(old_taxable,0), "old")
new_tax_slab = calculate_slab_tax(max(new_taxable,0), "new")

# Special income tax
special_old = stcg*0.15 + max((ltcg-100000),0)*0.10 + (lottery+crypto)*0.30
special_new = special_old

# Total tax
old_total = old_tax_slab + special_old
new_total = new_tax_slab + special_new

# Add cess
old_total_with_cess = old_total * 1.04
new_total_with_cess = new_total * 1.04

# Comparison table
data = {
    "Particulars": ["Gross Income","Total Deductions","Taxable Income","Tax from Slab","Tax from Special Income","Cess (4%)","Total Tax Payable"],
    "Old Regime": [gross_income, old_deductions, old_taxable, old_tax_slab, special_old, old_total*0.04, old_total_with_cess],
    "New Regime": [gross_income, standard_deduction, new_taxable, new_tax_slab, special_new, new_total*0.04, new_total_with_cess]
}

df = pd.DataFrame(data)
st.subheader("📊 Tax Comparison Table")
st.table(df.style.format({"Old Regime":"₹{:,.0f}","New Regime":"₹{:,.0f}"}))

# Savings highlight
savings = old_total_with_cess - new_total_with_cess
if savings > 0:
    better = "✅ New Regime is Better"
else:
    better = "✅ Old Regime is Better"

st.markdown(f"### 💡 Savings Difference: ₹{abs(savings):,.0f}")
st.success(better)

# Visuals
col1, col2 = st.columns(2)

with col1:
    fig = px.bar(x=["Old Regime","New Regime"], y=[old_total_with_cess,new_total_with_cess], 
                 text=[f"₹{old_total_with_cess:,.0f}",f"₹{new_total_with_cess:,.0f}"],
                 color=["Old Regime","New Regime"], title="Total Tax Payable", color_discrete_map={"Old Regime":"green","New Regime":"blue"})
    st.plotly_chart(fig, use_container_width=True)

with col2:
    pie_df = pd.DataFrame({"Type":["Slab Tax","Special Tax","Cess"],
                           "Old Regime":[old_tax_slab, special_old, old_total*0.04],
                           "New Regime":[new_tax_slab, special_new, new_total*0.04]})
    fig2 = px.pie(pie_df, values="Old Regime", names="Type", title="Tax Distribution - Old Regime")
    fig3 = px.pie(pie_df, values="New Regime", names="Type", title="Tax Distribution - New Regime")
    st.plotly_chart(fig2, use_container_width=True)
    st.plotly_chart(fig3, use_container_width=True)

st.caption("Built with ❤️ using Streamlit")
