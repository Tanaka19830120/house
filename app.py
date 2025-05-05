import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

# ✅ フォント指定（文字化け対策）
plt.rcParams['font.family'] = 'DejaVu Sans'

st.set_page_config(page_title="Housing Cost Comparison Simulator", layout="centered")

def calculate_monthly_payment(principal, annual_rate, years):
    r = annual_rate / 100 / 12
    n = years * 12
    if r == 0:
        return principal * 10000 / n
    return principal * 10000 * r * (1 + r) ** n / ((1 + r) ** n - 1)

st.title("🏡 Housing Cost Comparison: Apartment vs Ichijo Komuten")

st.sidebar.header("📊 Basic Settings")
years = st.sidebar.slider("Comparison period (years)", 10, 50, 35, key="years")

st.sidebar.subheader("🏢 Apartment")
apt_loan = st.sidebar.number_input("Remaining loan (万円)", value=2500, key="apt_loan")
apt_loan_years = st.sidebar.number_input("Years remaining", value=20, key="apt_loan_years")
apt_loan_rate = st.sidebar.number_input("Interest rate (%)", value=1.0, key="apt_loan_rate")
apt_kanri = st.sidebar.number_input("Monthly maintenance fee (万円)", value=1.2, key="apt_kanri")
apt_shuzen = st.sidebar.number_input("Monthly repair reserve (万円)", value=1.5, key="apt_shuzen")

st.sidebar.subheader("🏠 Ichijo Home")
ichijo_loan = st.sidebar.number_input("Loan amount (万円)", value=5000, key="ichijo_loan")
ichijo_loan_years = st.sidebar.number_input("Repayment period (years)", value=35, key="ichijo_loan_years")
ichijo_loan_rate = st.sidebar.number_input("Interest rate (%)", value=1.0, key="ichijo_loan_rate")
ichijo_utility = st.sidebar.number_input("Monthly utility costs (万円)", value=0.8, key="ichijo_utility")
ichijo_repair_year = st.sidebar.number_input("Repair year", value=20, key="ichijo_repair_year")
ichijo_repair_cost = st.sidebar.number_input("Repair cost (万円)", value=100, key="ichijo_repair_cost")

st.sidebar.subheader("📈 Shared Settings")
inflation_rate = st.sidebar.slider("Inflation rate (%)", 0.0, 5.0, 1.0, key="inflation_rate")
jutaku_kojo_years = st.sidebar.number_input("Loan deduction period (years)", value=10, key="kojo_years")
kojo_rate = st.sidebar.number_input("Deduction cashback rate (%)", value=1.0, key="kojo_rate")

# Calculation
apt_monthly = calculate_monthly_payment(apt_loan, apt_loan_rate, apt_loan_years)
ichijo_monthly = calculate_monthly_payment(ichijo_loan, ichijo_loan_rate, ichijo_loan_years)

apt_monthly_list = []
ichijo_monthly_list = []

for y in range(1, years + 1):
    inflator = (1 + inflation_rate / 100) ** (y - 1)

    apt_total = apt_monthly if y <= apt_loan_years else 0
    apt_total += (apt_kanri + apt_shuzen) * 10000 * inflator
    apt_monthly_list.append(apt_total)

    ichijo_total = ichijo_monthly if y <= ichijo_loan_years else 0
    ichijo_total += ichijo_utility * 10000
    if y == ichijo_repair_year:
        ichijo_total += ichijo_repair_cost * 10000 / 12
    if y <= jutaku_kojo_years:
        ichijo_total -= ichijo_loan * 10000 * kojo_rate / 100 / 12
    ichijo_monthly_list.append(ichijo_total)

apt_cumsum = [sum(apt_monthly_list[:i + 1]) for i in range(years)]
ichijo_cumsum = [sum(ichijo_monthly_list[:i + 1]) for i in range(years)]

# Graph
fig, ax = plt.subplots(2, 1, figsize=(10, 8))
x = list(range(1, years + 1))

# Monthly Payment
ax[0].plot(x, apt_monthly_list, label="Apartment", marker='o')
ax[0].plot(x, ichijo_monthly_list, label="Ichijo", marker='s')
ax[0].set_title("Monthly Payment")
ax[0].set_xlabel("Year")
ax[0].set_ylabel("JPY / Month")
ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax[0].legend()
ax[0].grid(True)

# Cumulative Payment
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
