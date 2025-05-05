import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

st.set_page_config(page_title="住宅コスト比較シミュレーター", layout="centered")

def calculate_monthly_payment(principal, annual_rate, years):
    r = annual_rate / 100 / 12
    n = years * 12
    if r == 0:
        return principal * 10000 / n
    return principal * 10000 * r * (1 + r) ** n / ((1 + r) ** n - 1)

st.title("🏡 マンション vs 一条工務店：コスト比較シミュレーター（改良版）")

# Sidebar Inputs
st.sidebar.header("📊 基本設定")
years = st.sidebar.slider("比較年数（年）", 10, 50, 35)

st.sidebar.subheader("🏢 マンションの設定")
apt_loan = st.sidebar.number_input("ローン残債（万円）", value=2000)
apt_loan_years = st.sidebar.number_input("ローン残年数（年）", value=27)
apt_loan_rate = st.sidebar.number_input("ローン金利（％）", value=1.0)
apt_kanri = st.sidebar.number_input("管理費（万円/月）", value=1.5)
apt_shuzen = st.sidebar.number_input("修繕積立金（万円/月）", value=2.5)
apt_parking = st.sidebar.number_input("駐車場代（万円/月）", value=1.0)
apt_utility = st.sidebar.number_input("光熱費（万円/月）", value=2.5)
apt_kojo_years = st.sidebar.number_input("住宅ローン控除期間（年）", value=2)
apt_kojo_rate = st.sidebar.number_input("住宅ローン控除還元率（％）", value=1)

st.sidebar.subheader("🏠 一条の設定")
ichijo_loan = st.sidebar.number_input("ローン借入額（万円）", value=5000)
ichijo_loan_years = st.sidebar.number_input("ローン返済期間（年）", value=35)
ichijo_loan_rate = st.sidebar.number_input("ローン金利（％）", value=1)
ichijo_utility = st.sidebar.number_input("光熱費（万円/月）", value=0.5)
ichijo_solar = st.sidebar.number_input("太陽光売電収入（万円/月）", value=2.0)
ichijo_repair_year = st.sidebar.number_input("定期修繕の年数", value=20)
ichijo_repair_cost = st.sidebar.number_input("定期修繕費（万円）", value=100)
ichijo_kojo_years = st.sidebar.number_input("住宅ローン控除期間（年）", value=15)
ichijo_kojo_rate = st.sidebar.number_input("住宅ローン控除還元率（％）", value=0.75)

st.sidebar.subheader("📈 共通設定")
inflation_rate = st.sidebar.slider("インフレ率（％）", 0.0, 5.0, 1.0)

# Monthly loan payments
apt_monthly = calculate_monthly_payment(apt_loan, apt_loan_rate, apt_loan_years)
ichijo_monthly = calculate_monthly_payment(ichijo_loan, ichijo_loan_rate, ichijo_loan_years)

apt_yearly_list = []
ichijo_yearly_list = []

for y in range(1, years + 1):
    inflator = (1 + inflation_rate / 100) ** (y - 1)

    # Mansion yearly
    apt_total = apt_monthly * 12 if y <= apt_loan_years else 0
    apt_total += (apt_kanri + apt_shuzen + apt_parking + apt_utility) * 10000 * 12 * inflator
    if y <= apt_kojo_years:
        apt_total -= apt_loan * 10000 * apt_kojo_rate / 100
    apt_yearly_list.append(apt_total)

    # Ichijo yearly
    ichijo_total = ichijo_monthly * 12 if y <= ichijo_loan_years else 0
    ichijo_total += (ichijo_utility * inflator - ichijo_solar) * 10000 * 12
    if y == ichijo_repair_year:
        ichijo_total += ichijo_repair_cost * 10000
    if y <= ichijo_kojo_years:
        ichijo_total -= ichijo_loan * 10000 * ichijo_kojo_rate / 100
    ichijo_yearly_list.append(ichijo_total)

apt_cumsum = [sum(apt_yearly_list[:i + 1]) for i in range(years)]
ichijo_cumsum = [sum(ichijo_yearly_list[:i + 1]) for i in range(years)]

# DataFrame
df = pd.DataFrame({
    "Year": list(range(1, years + 1)),
    "マンション 年間支出 (円)": apt_yearly_list,
    "一条 年間支出 (円)": ichijo_yearly_list,
    "マンション 累積支出 (円)": apt_cumsum,
    "一条 累積支出 (円)": ichijo_cumsum,
})

st.subheader("📄 年別支払い内訳")
st.dataframe(df.style.format({col: "{:,.0f}" for col in df.columns if col != "Year"}), use_container_width=True)

# グラフ描画
fig, ax = plt.subplots()
ax.plot(df["Year"], df["マンション 年間支出 (円)"], label="マンション 年間", linestyle="--")
ax.plot(df["Year"], df["一条 年間支出 (円)"], label="一条 年間", linestyle="--")
ax.plot(df["Year"], df["マンション 累積支出 (円)"], label="マンション 累積")
ax.plot(df["Year"], df["一条 累積支出 (円)"], label="一条 累積")
ax.set_xlabel("年")
ax.set_ylabel("支出額（円）")
ax.set_title("年間支出＆累積支出グラフ")
ax.legend()
st.pyplot(fig)

# Summary
diff = apt_cumsum[-1] - ichijo_cumsum[-1]
winner = "一条工務店" if diff > 0 else "マンション"
savings = abs(diff) / 10000

st.markdown(f"### 💡 {years}年後、**{winner}** の方が **{savings:,.0f}万円** お得です。")
