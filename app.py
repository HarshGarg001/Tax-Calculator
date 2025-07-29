import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Tax Calculator", layout="wide")

# --- Custom Toggle Button ---
toggle_html = """
<style>
.toggle-container {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 10px;
}
.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}
.switch input {display:none;}
.slider {
  position: absolute;
  cursor: pointer;
  top: 0; left: 0; right: 0; bottom: 0;
  background-color: #002B36;
  transition: .4s;
  border-radius: 34px;
}
.slider:before {
  position: absolute;
  content: "🌙";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: #00AEEF;
  transition: .4s;
  border-radius: 50%;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 16px;
}
input:checked + .slider {
  background-color: #FFE79A;
}
input:checked + .slider:before {
  transform: translateX(26px);
  content: "☀️";
  background-color: #FFD43B;
}
</style>

<div class="toggle-container">
  <label class="switch">
    <input type="checkbox" id="themeToggle">
    <span class="slider"></span>
  </label>
</div>

<script>
const themeToggle = window.parent.document.getElementById("themeToggle");
themeToggle.addEventListener("change", function() {
    window.parent.postMessage({theme: this.checked ? "light" : "dark"}, "*");
});
</script>
"""
st.markdown(toggle_html, unsafe_allow_html=True)

if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

theme = "plotly_dark" if st.session_state["theme"] == "dark" else "plotly_white"

# --- Sidebar Inputs ---
with st.sidebar:
    st.header("💡 Enter Your Details")
    salary = st.number_input("Salary Income (₹)", min_value=0, step=1000)
    other_income = st.number_input("Other Income (₹)", min_value=0, step=1000)

    st.subheader("Special Income")
    stcg = st.number_input("STCG (15%)", min_value=0, step=1000)
    ltcg = st.number_input("LTCG (>₹1L @10%)", min_value=0, step=1000)
    lottery = st.number_input("Lottery (30%+Cess)", min_value=0, step=1000)
    crypto = st.number_input("Crypto Income (30%+Cess)", min_value=0, step=1000)

    st.subheader("Deductions (Old Regime)")
    ded_80C = st.number_input("80C", min_value=0, step=1000)
    ded_80D = st.number_input("80D", min_value=0, step=1000)
    ded_hra = st.number_input("HRA Exemption", min_value=0, step=1000)

# --- Tax Calculation Logic ---
def calculate_tax(salary, other_income, stcg, ltcg, lottery, crypto, deductions, regime):
    gross_total = salary + other_income
    stcg_tax = stcg * 0.15
    ltcg_tax = max(ltcg - 100000, 0) * 0.10
    lottery_tax = lottery * 0.30 * 1.04
    crypto_tax = crypto * 0.30 * 1.04
    special_tax = stcg_tax + ltcg_tax + lottery_tax + crypto_tax

    if regime == "Old":
        total_deductions = 50000 + deductions
        slabs = [(250000, 0.05), (500000, 0.20), (float("inf"), 0.30)]
    else:
        total_deductions = 50000
        slabs = [(300000, 0.05), (600000, 0.10), (900000, 0.15),
                 (1200000, 0.20), (1500000, 0.25), (float("inf"), 0.30)]

    taxable_income = max(gross_total - total_deductions, 0)
    remaining = taxable_income
    last_limit = 0
    slab_tax = 0
    for limit, rate in slabs:
        taxable = min(remaining, limit - last_limit)
        slab_tax += taxable * rate
        remaining -= taxable
        last_limit = limit
        if remaining <= 0:
            break

    total_tax = slab_tax + special_tax
    rebate = 0
    if taxable_income <= 500000:
        rebate = min(total_tax, 12500)
    total_tax += (total_tax - rebate) * 0.04

    return gross_total, total_deductions, taxable_income, slab_tax, special_tax, rebate, total_tax

old_vals = calculate_tax(salary, other_income, stcg, ltcg, lottery, crypto, ded_80C+ded_80D+ded_hra, "Old")
new_vals = calculate_tax(salary, other_income, stcg, ltcg, lottery, crypto, 0, "New")

# --- Comparison Table ---
data = {
    "Particulars": ["Gross Income", "Total Deductions", "Taxable Income", 
                    "Tax from Slab", "Tax from Special Income", "Cess (4%)", "Total Tax Payable"],
    "Old Regime": [old_vals[0], old_vals[1], old_vals[2], old_vals[3], old_vals[4], (old_vals[6]-old_vals[3]-old_vals[4]), old_vals[6]],
    "New Regime": [new_vals[0], new_vals[1], new_vals[2], new_vals[3], new_vals[4], (new_vals[6]-new_vals[3]-new_vals[4]), new_vals[6]]
}
df = pd.DataFrame(data)
st.markdown("### 📊 Tax Comparison Table")
st.dataframe(df, use_container_width=True)

savings = old_vals[6] - new_vals[6]
if savings > 0:
    st.success(f"✅ New Regime is Better → You Save ₹{savings:,.0f}")
elif savings < 0:
    st.error(f"✅ Old Regime is Better → You Save ₹{abs(savings):,.0f}")
else:
    st.info("Both regimes have the same tax.")

# --- Charts ---
col1, col2 = st.columns(2)
with col1:
    fig = px.bar(
        x=["Old Regime", "New Regime"], 
        y=[old_vals[6], new_vals[6]], 
        labels={"x": "Regime", "y": "Total Tax"},
        color=["Old Regime", "New Regime"],
        title="Total Tax Payable",
        color_discrete_map={"Old Regime": "red", "New Regime": "green"},
        template=theme
    )
    st.plotly_chart(fig, use_container_width=True)

with col2:
    old_dist = {"Slab Tax": old_vals[3], "Special Tax": old_vals[4], "Cess": old_vals[6]-old_vals[3]-old_vals[4]}
    new_dist = {"Slab Tax": new_vals[3], "Special Tax": new_vals[4], "Cess": new_vals[6]-new_vals[3]-new_vals[4]}
    fig2 = px.pie(names=list(old_dist.keys()), values=list(old_dist.values()), title="Old Regime Tax Distribution", template=theme)
    st.plotly_chart(fig2, use_container_width=True)

    fig3 = px.pie(names=list(new_dist.keys()), values=list(new_dist.values()), title="New Regime Tax Distribution", template=theme)
    st.plotly_chart(fig3, use_container_width=True)
