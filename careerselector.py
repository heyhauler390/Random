import streamlit as st
import pandas as pd
import altair as alt

def with_monthly_labels(data_dict):
    """
    Takes a dict { 'Label': annual_cost, ... } and returns a dict
    where each key is updated to include the monthly cost in parentheses.
    Example:
      "Rent an Apartment" -> "Rent an Apartment ($1,000/mo)" for annual_cost=12000
    """
    updated = {}
    for name, annual_cost in data_dict.items():
        monthly_cost = annual_cost / 12
        updated_key = f"{name} (${monthly_cost:,.0f}/mo)"
        updated[updated_key] = annual_cost
    return updated

def compute_taxes(income):
    """
    A simplified tiered tax function (not real tax law!).
    Brackets:
      - 10% for first $20k
      - 15% for next $40k (20k - 60k)
      - 20% for next $60k (60k - 120k)
      - 25% above 120k
    """
    if income <= 0:
        return 0

    tax = 0.0
    remaining = income

    # Bracket 1: Up to 20k at 10%
    bracket1_limit = 20000
    bracket1_rate = 0.10

    if remaining > bracket1_limit:
        tax += bracket1_limit * bracket1_rate
        remaining -= bracket1_limit
    else:
        tax += remaining * bracket1_rate
        remaining = 0

    if remaining <= 0:
        return tax

    # Bracket 2: 20k to 60k at 15%
    bracket2_limit = 40000
    bracket2_rate = 0.15

    if remaining > bracket2_limit:
        tax += bracket2_limit * bracket2_rate
        remaining -= bracket2_limit
    else:
        tax += remaining * bracket2_rate
        remaining = 0

    if remaining <= 0:
        return tax

    # Bracket 3: 60k to 120k at 20%
    bracket3_limit = 60000
    bracket3_rate = 0.20

    if remaining > bracket3_limit:
        tax += bracket3_limit * bracket3_rate
        remaining -= bracket3_limit
    else:
        tax += remaining * bracket3_rate
        remaining = 0

    if remaining <= 0:
        return tax

    # Bracket 4: Above 120k at 25%
    bracket4_rate = 0.25
    tax += remaining * bracket4_rate

    return tax

def main():
    st.title("College Financial Decisions App (With Taxes & Correct Waterfall)")

    st.write("""
    This app demonstrates:
    - Choosing a career (annual salary).
    - Accounting for taxes using simple brackets.
    - Selecting various expenses (housing, vehicle, groceries, etc.),
      each labeled with monthly costs.
    - Retirement savings as a percentage of salary.
    - **A waterfall chart that doesn't double-count** the final discretionary income.
    """)

    # -------------------------------
    # 1. Define the raw data dicts
    # -------------------------------
    career_data_raw = {
        "Software Engineer": 90000,
        "Teacher": 45000,
        "Data Scientist": 100000,
        "Nurse": 65000,
        "Accountant": 55000,
        "Marketing Specialist": 60000
    }
    housing_data_raw = {
        "Rent an Apartment": 12000,
        "Buy a Cheap House": 18000,
        "Buy a Nice House": 30000
    }
    vehicle_data_raw = {
        "No Car (Public Transport)": 1000,
        "Used Economy Car": 3000,
        "New Economy Car": 5000,
        "SUV": 7000,
        "Luxury Car": 10000
    }
    groceries_data_raw = {
        "Minimal Groceries": 2400,
        "Basic Groceries": 3600,
        "Premium Groceries": 6000
    }
    phone_data_raw = {
        "Basic Phone Plan": 300,
        "Standard Phone Plan": 600,
        "Unlimited Premium": 1200
    }
    utilities_data_raw = {
        "Low Utilities": 1800,
        "Medium Utilities": 3000,
        "High Utilities": 4800
    }
    insurance_data_raw = {
        "Basic Insurance": 1200,
        "Standard Insurance": 2400,
        "Comprehensive Insurance": 4800
    }
    loan_data_raw = {
        "No Loans": 0,
        "Low Repayment": 3000,
        "Medium Repayment": 6000,
        "High Repayment": 12000
    }
    entertainment_data_raw = {
        "No Subscriptions": 0,
        "Basic Streaming & Activities": 600,
        "Moderate Entertainment": 1500,
        "High Entertainment": 3000
    }
    retirement_data = {
        "None (0%)": 0.00,
        "5% of Salary": 0.05,
        "10% of Salary": 0.10,
        "15% of Salary": 0.15,
        "20% of Salary": 0.20
    }

    # -------------------------------
    # 2. Convert to monthly-labeled
    # -------------------------------
    career_data = with_monthly_labels(career_data_raw)
    housing_data = with_monthly_labels(housing_data_raw)
    vehicle_data = with_monthly_labels(vehicle_data_raw)
    groceries_data = with_monthly_labels(groceries_data_raw)
    phone_data = with_monthly_labels(phone_data_raw)
    utilities_data = with_monthly_labels(utilities_data_raw)
    insurance_data = with_monthly_labels(insurance_data_raw)
    loan_data = with_monthly_labels(loan_data_raw)
    entertainment_data = with_monthly_labels(entertainment_data_raw)
    # Retirement is percentage-based, so we skip with_monthly_labels.

    # -------------------------------
    # 3. User Selections
    # -------------------------------
    st.subheader("1. Choose a Career (Annual Salary)")
    selected_career = st.selectbox("Career Path:", list(career_data.keys()))
    annual_salary = career_data[selected_career]

    st.subheader("2. Housing")
    selected_housing = st.selectbox("Home Option:", list(housing_data.keys()))
    housing_cost = housing_data[selected_housing]

    st.subheader("3. Vehicle")
    selected_vehicle = st.selectbox("Vehicle Option:", list(vehicle_data.keys()))
    vehicle_cost = vehicle_data[selected_vehicle]

    st.subheader("4. Groceries")
    selected_groceries = st.selectbox("Grocery Budget:", list(groceries_data.keys()))
    groceries_cost = groceries_data[selected_groceries]

    st.subheader("5. Phone Plan")
    selected_phone = st.selectbox("Phone Plan:", list(phone_data.keys()))
    phone_cost = phone_data[selected_phone]

    st.subheader("6. Utilities")
    selected_utilities = st.selectbox("Utilities:", list(utilities_data.keys()))
    utilities_cost = utilities_data[selected_utilities]

    st.subheader("7. Insurance")
    selected_insurance = st.selectbox("Insurance:", list(insurance_data.keys()))
    insurance_cost = insurance_data[selected_insurance]

    st.subheader("8. College Loan")
    selected_loan = st.selectbox("Loan Repayment:", list(loan_data.keys()))
    loan_cost = loan_data[selected_loan]

    st.subheader("9. Entertainment")
    selected_entertainment = st.selectbox("Entertainment:", list(entertainment_data.keys()))
    entertainment_cost = entertainment_data[selected_entertainment]

    st.subheader("10. Retirement Savings (as % of Salary)")
    selected_retirement = st.selectbox("Contribution:", list(retirement_data.keys()))
    retirement_fraction = retirement_data[selected_retirement]
    retirement_cost = annual_salary * retirement_fraction

    # -------------------------------
    # 4. Taxes
    # -------------------------------
    tax_amount = compute_taxes(annual_salary)

    # -------------------------------
    # 5. Calculate Discretionary Income
    # -------------------------------
    total_expenses = (
        housing_cost + vehicle_cost + groceries_cost + phone_cost +
        utilities_cost + insurance_cost + loan_cost + entertainment_cost +
        retirement_cost
    )
    discretionary_income = annual_salary - tax_amount - total_expenses

    # -------------------------------
    # 6. Show Summary
    # -------------------------------
    st.write("---")
    st.write("## Summary of Your Choices")

    st.write(f"- **Career**: {selected_career} => Annual Salary: ${annual_salary:,.0f}")
    st.write(f"- **Taxes**: ${tax_amount:,.0f}")
    st.write(f"- **Housing**: {selected_housing} => ${housing_cost:,.0f}")
    st.write(f"- **Vehicle**: {selected_vehicle} => ${vehicle_cost:,.0f}")
    st.write(f"- **Groceries**: {selected_groceries} => ${groceries_cost:,.0f}")
    st.write(f"- **Phone**: {selected_phone} => ${phone_cost:,.0f}")
    st.write(f"- **Utilities**: {selected_utilities} => ${utilities_cost:,.0f}")
    st.write(f"- **Insurance**: {selected_insurance} => ${insurance_cost:,.0f}")
    st.write(f"- **College Loan**: {selected_loan} => ${loan_cost:,.0f}")
    st.write(f"- **Entertainment**: {selected_entertainment} => ${entertainment_cost:,.0f}")
    st.write(f"- **Retirement**: {selected_retirement} => ${retirement_cost:,.0f}")

    if discretionary_income < 0:
        st.error(f"**Discretionary Income: -${abs(discretionary_income):,.0f}**")
    else:
        st.success(f"**Discretionary Income: ${discretionary_income:,.0f}**")

    # -------------------------------
    # 7. Waterfall Chart WITHOUT Double-Counting
    # -------------------------------
    # We set the final "Discretionary Income" step to 0,
    # and then we label that bar with the actual leftover amount.

    data_steps = [
        {"Category": "Starting Salary",   "Amount": annual_salary},
        {"Category": "Taxes",             "Amount": -tax_amount},
        {"Category": "Housing",           "Amount": -housing_cost},
        {"Category": "Vehicle",           "Amount": -vehicle_cost},
        {"Category": "Groceries",         "Amount": -groceries_cost},
        {"Category": "Phone",             "Amount": -phone_cost},
        {"Category": "Utilities",         "Amount": -utilities_cost},
        {"Category": "Insurance",         "Amount": -insurance_cost},
        {"Category": "College Loan",      "Amount": -loan_cost},
        {"Category": "Entertainment",     "Amount": -entertainment_cost},
        {"Category": "Retirement",        "Amount": -retirement_cost},
        # Final bar is 0 to avoid adding leftover to cumsum again
        {"Category": "Discretionary Income", "Amount": 0},
    ]

    df_steps = pd.DataFrame(data_steps)

    # Standard cumsum approach
    df_steps["Cumulative"] = df_steps["Amount"].cumsum()
    df_steps["Start"] = df_steps["Cumulative"].shift(1, fill_value=0)
    df_steps["End"] = df_steps["Cumulative"]

    # We'll create a separate "Label" column for the text on each bar.
    # The final bar label = discretionary_income, everything else = cumsum.
    def get_label_value(row):
        if row["Category"] == "Discretionary Income":
            return discretionary_income
        else:
            return row["Cumulative"]

    df_steps["Label"] = df_steps.apply(get_label_value, axis=1)

    # Color logic
    def pick_color(cat, val):
        if cat == "Starting Salary":
            return "green"
        elif cat == "Discretionary Income":
            # If leftover is negative, use red; otherwise, blue
            return "blue" if discretionary_income >= 0 else "red"
        else:
            return "red"  # All other steps are negative subtractions

    df_steps["Color"] = df_steps.apply(lambda r: pick_color(r["Category"], r["Amount"]), axis=1)

    # Build the chart
    base = alt.Chart(df_steps)

    bars = base.mark_bar().encode(
        x=alt.X("Category:N", sort=None, title=""),
        y=alt.Y("Start:Q", title="Annual Amount (USD)"),
        y2="End:Q",
        color=alt.Color("Color:N", scale=None),
        tooltip=[
            alt.Tooltip("Category:N",      title="Category"),
            alt.Tooltip("Amount:Q",        title="Step Amount", format=",.0f"),
            alt.Tooltip("Cumulative:Q",    title="Cumulative",  format=",.0f")
        ]
    )

    labels = base.mark_text(
        dy=-5,
        color="black",
        fontWeight="bold"
    ).encode(
        x=alt.X("Category:N", sort=None),
        y=alt.Y("End:Q"),
        # Use the "Label" column for text, so final bar shows leftover
        text=alt.Text("Label:Q", format=",.0f")
    )

    waterfall_chart = (bars + labels).properties(
        width=750,
        height=400
    )

    st.write("---")
    st.write("## Waterfall Chart (Income, Taxes, Expenses)")
    st.altair_chart(waterfall_chart, use_container_width=True)

if __name__ == "__main__":
    main()
