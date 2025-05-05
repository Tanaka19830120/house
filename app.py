import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rcParams['font.family'] = 'DejaVu Sans'  # 文字化け対策：英語フォントに限定

st.set_page_config(page_title="住宅コスト比較シミュレーター", layout="centered")

def calculate_monthly_payment(principal, annual_rate, years):
    r = annual_rate / 100 / 12
    n = years * 12
    if r == 0:
        return principal * 10000 / n
    return principal * 10000 * r * (1 + r) ** n / ((1 + r) ** n - 1)

st.title("🏡 マンション vs 一条工務店：コスト比較シミュレーター")

st.sidebar.header("📊 基本設定")
years = st.sidebar.slider("比較年数（年）", 10, 50, 35)

#🏢マンション
st.sidebar.subheader("🏢 マンションの設定")
apt_loan = st.sidebar.number_input("ローン残債（万円）", value=2500)
apt_loan_years = st.sidebar.number_input("ローン残年数（年）", value=20)
apt_loan_rate = st.sidebar.number_input("ローン金利（％）", value=1.0)
apt_kanri = st.sidebar.number_input("管理費（万円/月）", value=1.2)
apt_shuzen = st.sidebar.number_input("修繕積立金（万円/月）", value=1.5)
apt_parking = st.sidebar.number_input("駐車場代（万円/月）", value=1.0)

#🏠一条工務店
st.sidebar.subheader("🏠 一条の設定")
ichijo_loan = st.sidebar.number_input("借入額（万円）", value=5000)
ichijo_loan_years = st.sidebar.number_input("返済期間（年）", value=35)
ichijo_loan_rate = st.sidebar.number_input("ローン金利（％）", value=1.0)
ichijo_utility = st.sidebar.number_input("光熱費（万円/月）", value=0.8)
ichijo_solar_income = st.sidebar.number_input("太陽光売電収入（万円/月）", value=0.5)
ichijo_repair_year = st.sidebar.number_input("定期修繕実施年", value=20)
ichijo_repair_cost = st.sidebar.number_input("定期修繕費用（万円）", value=100)

#💰住宅ローン控除
st.sidebar.subheader("💰 住宅ローン控除の設定")

st.sidebar.markdown("**🏢 マンションの住宅ローン控除**")
apt_kojo_years = st.sidebar.number_input("控除適用年数（年）", value=10, key="apt_kojo_years")
apt_kojo_rate = st.sidebar.number_input("還元率（％）", value=1.0, key="apt_kojo_rate")

st.sidebar.markdown("**🏠 一条の住宅ローン控除**")
ichijo_kojo_years = st.sidebar.number_input("控除適用年数（年）", value=10, key="ichijo_kojo_years")
ichijo_kojo_rate = st.sidebar.number_input("還元率（％）", value=1.0, key="ichijo_kojo_rate")

#📈共通インフレ設定
st.sidebar.subheader("📈 インフレ設定")
inflation_rate = st.sidebar.slider("インフレ率（％）", 0.0, 5.0, 1.0)

# 支払い計算
apt_monthly = calculate_monthly_payment(apt_loan, apt_loan_rate, apt_loan_years)
ichijo_monthly = calculate_monthly_payment(ichijo_loan, ichijo_loan_rate, ichijo_loan_years)

apt_monthly_list = []
ichijo_monthly_list = []

for y in range(1, years + 1):
    inflator = (1 + inflation_rate / 100) ** (y - 1)

    # マンション
    apt_total = apt_monthly if y <= apt_loan_years else 0
    apt_total += (apt_kanri + apt_shuzen) * 10000 * inflator
    apt_total += apt_parking * 10000
    if y <= apt_kojo_years:
        apt_total -= apt_loan * 10000 * apt_kojo_rate / 100 / 12
    apt_monthly_list.append(apt_total)

    # 一条
    ichijo_total = ichijo_monthly if y <= ichijo_loan_years else 0
    ichijo_total += ichijo_utility * 10000
    ichijo_total -= ichijo_solar_income * 10000
    if y == ichijo_repair_year:
        ichijo_total += ichijo_repair_cost * 10000 / 12
    if y <= ichijo_kojo_years:
        ichijo_total -= ichijo_loan * 10000 * ichijo_kojo_rate / 100 / 12
    ichijo_monthly_list.append(ichijo_total)

# 累積計算
apt_cumsum = [sum(apt_monthly_list[:i + 1]) for i in range(years)]
ichijo_cumsum = [sum(ichijo_monthly_list[:i + 1]) for i in range(years)]

# グラフ表示
fig, ax = plt.subplots(2, 1, figsize=(10, 8))
x = list(range(1, years + 1))

# 月々
ax[0].plot(x, apt_monthly_list, label="Apartment", marker='o')
ax[0].plot(x, ichijo_monthly_list, label="Ichijo", marker='s')
ax[0].set_title("Monthly Payment")
ax[0].set_xlabel("Year")
ax[0].set_ylabel("JPY / Month")
ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax[0].legend()
ax[0].grid(True)

# 累積
ax[1].plot(x, apt_cumsum, label="Apartment", marker='o')
ax[1].plot(x, ichijo_cumsum, label="Ichijo", marker='s')
ax[1].set_title("Cumulative Payment")
ax[1].set_xlabel("Year")
ax[1].set_ylabel("Cumulative JPY")
ax[1].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax[1].legend()
ax[1].grid(True)

plt.tight_layout()
st.pyplot(fig)
