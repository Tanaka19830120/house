import streamlit as st
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

plt.rcParams['font.family'] = 'DejaVu Sans'

st.set_page_config(page_title="Housing Cost Comparison", layout="centered")

def calculate_monthly_payment(principal, annual_rate, years):
    r = annual_rate / 100 / 12
    n = years * 12
    if r == 0:
        return principal * 10000 / n
    return principal * 10000 * r * (1 + r) ** n / ((1 + r) ** n - 1)

st.title("🏡 Housing Cost Simulator: Apartment vs Ichijo")

st.sidebar.header("📊 Settings")
years = st.sidebar.slider("Comparison Period (Years)", 10, 50, 35, key="years")

# Apartment settings
st.sidebar.subheader("🏢 Apartment")
apt_loan = st.sidebar.number_input("Remaining Loan (10,000 JPY)", value=2500, key="apt_loan")
apt_loan_years = st.sidebar.number_input("Loan Remaining Years", value=20, key="apt_loan_years")
apt_loan_rate = st.sidebar.number_input("Loan Rate (%)", value=1.0, key="apt_loan_rate")
apt_kanri = st.sidebar.number_input("Monthly Maintenance (10,000 JPY)", value=1.2, key="apt_kanri")
apt_shuzen = st.sidebar.number_input("Repair Fund (10,000 JPY)", value=1.5, key="apt_shuzen")
apt_parking = st.sidebar.number_input("Parking Fee (10,000 JPY)", value=1.0, key="apt_parking")

# Ichijo settings
st.sidebar.subheader("🏠 Ichijo")
ichijo_loan = st.sidebar.number_input("Loan Amount (10,000 JPY)", value=5000, key="ichijo_loan")
ichijo_loan_years = st.sidebar.number_input("Repayment Years", value=35, key="ichijo_loan_years")
ichijo_loan_rate = st.sidebar.number_input("Loan Rate (%)", value=1.0, key="ichijo_loan_rate")
ichijo_utility = st.sidebar.number_input("Utility Cost (10,000 JPY)", value=0.8, key="ichijo_utility")
ichijo_repair_year = st.sidebar.number_input("Repair Year", value=20, key="ichijo_repair_year")
ichijo_repair_cost = st.sidebar.number_input("Repair Cost (10,000 JPY)", value=100, key="ichijo_repair_cost")
ichijo_solar_income = st.sidebar.number_input("Solar Income (10,000 JPY)", value=0.5, key="ichijo_solar_income")

# Shared
st.sidebar.subheader("📈 Common Settings")
inflation_rate = st.sidebar.slider("Inflation Rate (%)", 0.0, 5.0, 1.0, key="inflation_rate")
jutaku_kojo_years = st.sidebar.number_input("Tax Deduction Years", value=10, key="kojo_years")
kojo_rate = st.sidebar.number_input("Deduction Rate (%)", value=1.0, key="kojo_rate")

# Calculation
apt_monthly = calculate_monthly_payment(apt_loan, apt_loan_rate, apt_loan_years)
ichijo_monthly = calculate_monthly_payment(ichijo_loan, ichijo_loan_rate, ichijo_loan_years)

apt_monthly_list = []
ichijo_monthly_list = []

for y in range(1, years + 1):
    inflator = (1 + inflation_rate / 100) ** (y - 1)

    apt_total = apt_monthly if y <= apt_loan_years else 0
    apt_total += (apt_kanri + apt_shuzen + apt_parking) * 10000 * inflator
    apt_monthly_list.append(apt_total)

    ichijo_total = ichijo_monthly if y <= ichijo_loan_years else 0
    ichijo_total += ichijo_utility * 10000
    ichijo_total -= ichijo_solar_income * 10000
    if y == ichijo_repair_year:
        ichijo_total += ichijo_repair_cost * 10000 / 12
    if y <= jutaku_kojo_years:
        ichijo_total -= ichijo_loan * 10000 * kojo_rate / 100 / 12
    ichijo_monthly_list.append(ichijo_total)

apt_cumsum = [sum(apt_monthly_list[:i + 1]) for i in range(years)]
ichijo_cumsum = [sum(ichijo_monthly_list[:i + 1]) for i in range(years)]

# Plot
fig, ax = plt.subplots(2, 1, figsize=(10, 8))
x = list(range(1, years + 1))

# Monthly payments
ax[0].plot(x, apt_monthly_list, label="Apartment", marker='o')
ax[0].plot(x, ichijo_monthly_list, label="Ichijo", marker='s')
ax[0].set_title("Monthly Payment")
ax[0].set_xlabel("Year")
ax[0].set_ylabel("JPY / Month")
ax[0].yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
ax[0].legend()
ax[0].grid(True)

# Cumulative payments
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
