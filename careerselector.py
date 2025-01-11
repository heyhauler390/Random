import streamlit as st
import pandas as pd
import altair as alt

###############################################################################
# 1. Helper Functions
###############################################################################
def with_monthly_and_annual_labels(data_dict):
    """
    Takes a dict { 'Label': annual_cost, ... }
    Returns a dict where each key includes monthly & annual cost:
      e.g. "Rent an Apartment ($1,000/mo, $12,000/yr)"
    """
    updated = {}
    for name, annual_cost in data_dict.items():
        monthly_cost = annual_cost / 12
        updated_key = f"{name} (${monthly_cost:,.0f}/mo, ${annual_cost:,.0f}/yr)"
        updated[updated_key] = annual_cost
    return updated

def compute_taxes(income):
    """
    Simplified tiered tax function (not real tax law!):
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
    st.title("Financial Decisions App with Family Toggle & Monthly Costs")

    st.write("""
    
    """)

    ############################################################################
    # 2. FAMILY STATUS SELECTION
    ############################################################################
    family_status = st.selectbox(
        "Select Your Family Status:",
        ["Single", "Family with kids"]
    )

    # This choice will affect groceries cost, medical cost, etc.

    ############################################################################
    # 3. DEFINE RAW DATA DICTS (WITHOUT monthly/annual labels yet)
    ############################################################################
    # 3.1 Career Data
    career_data_raw = {
        "Software Engineer": 90000,
        "Teacher": 45000,
        "Data Scientist": 100000,
        "Nurse": 65000,
        "Accountant": 55000,
        "Marketing Specialist": 60000
    }

    # 3.2 Housing (plus associated mandatory home insurance)
    housing_data_raw = {
        # We'll store (annual_rent_or_mortgage, annual_home_insurance)
        "Rent an Apartment": (12000, 150),    # renters insurance
        "Buy a Cheap House": (18000, 600),    # homeowners insurance
        "Buy a Nice House": (30000, 1000)     # homeowners insurance
    }

    # 3.3 Vehicle
    # For each vehicle, define (annual_payment, mpg_estimate) 
    # so we can compute gas cost separately.
    vehicle_data_raw = {
        "No Car (Public Transport)": (1000, 0),   # no mpg => no gas cost
        "Used Economy Car": (3000, 30),
        "New Economy Car": (5000, 28),
        "SUV": (7000, 20),
        "Luxury Car": (10000, 18)
    }

    # 3.4 Groceries
    # Single vs. Family: we define different annual costs
    if family_status == "Single":
        groceries_dict_raw = {
            "Minimal Groceries": 2400,
            "Basic Groceries": 3600,
            "Premium Groceries": 6000
        }
    else:  # Family with kids
        groceries_dict_raw = {
            "Minimal Groceries": 3600,   # e.g., +$1,200 for kids
            "Basic Groceries": 5400,
            "Premium Groceries": 9000
        }

    # 3.5 Medical Insurance 
    # Single vs. Family rates
    if family_status == "Single":
        medical_data_raw = {
            "Free": 0,
            "Basic": 2000,
            "Premium": 5000
        }
    else:
        medical_data_raw = {
            "Free": 0,
            "Basic": 3500,   # e.g., +$1,500 for kids
            "Premium": 7000
        }

    # 3.6 Phone Plan
    phone_data_raw = {
        "Basic Phone Plan": 300,
        "Standard Phone Plan": 600,
        "Unlimited Premium": 1200
    }

    # 3.7 Utilities
    utilities_data_raw = {
        "Low Utilities": 1800,
        "Medium Utilities": 3000,
        "High Utilities": 4800
    }

    # 3.8 Loan (College Loan)
    loan_data_raw = {
        "No Loans": 0,
        "Low Repayment": 3000,
        "Medium Repayment": 6000,
        "High Repayment": 12000
    }

    # 3.9 Entertainment
    entertainment_data_raw = {
        "No Subscriptions": 0,
        "Basic Streaming & Activities": 600,
        "Moderate Entertainment": 1500,
        "High Entertainment": 3000
    }

    # 3.10 Retirement
    retirement_data = {
        "None (0%)": 0.00,
        "5% of Salary": 0.05,
        "10% of Salary": 0.10,
        "15% of Salary": 0.15,
        "20% of Salary": 0.20
    }

    # 3.11 Childcare (Optional: Show only if family with kids)
    # You can treat this as a separate cost or embed it in groceries, etc.
    childcare_data_raw = {
        "No Childcare": 0,
        "Minimal Daycare": 3000,
        "Premium Daycare": 6000
    }

    ############################################################################
    # 4. Convert to monthly+annual labels (where applicable)
    ############################################################################
    # For housing, we have 2 values per option => must handle carefully:
    # We'll only label the main rent/mortgage cost; insurance is hidden from user.
    housing_labeled = {}
    for label, (annual_housing, _) in housing_data_raw.items():
        monthly_cost = annual_housing / 12
        new_key = f"{label} (${monthly_cost:,.0f}/mo, ${annual_housing:,.0f}/yr)"
        housing_labeled[new_key] = label  # store the 'label' so we can look up real cost

    # For vehicle, we have (annual_payment, mpg)
    vehicle_labeled = {}
    for label, (annual_payment, mpg) in vehicle_data_raw.items():
        monthly_cost = annual_payment / 12
        new_key = f"{label} (${monthly_cost:,.0f}/mo, ${annual_payment:,.0f}/yr)"
        vehicle_labeled[new_key] = label

    # Standard use of with_monthly_and_annual_labels for single-value dicts
    career_data = with_monthly_and_annual_labels(career_data_raw)
    groceries_data = with_monthly_and_annual_labels(groceries_dict_raw)
    medical_data = with_monthly_and_annual_labels(medical_data_raw)
    phone_data = with_monthly_and_annual_labels(phone_data_raw)
    utilities_data = with_monthly_and_annual_labels(utilities_data_raw)
    loan_data = with_monthly_and_annual_labels(loan_data_raw)
    entertainment_data = with_monthly_and_annual_labels(entertainment_data_raw)
    # retirement_data is % - no monthly/annual label function 
    # childcare (only if family)
    if family_status == "Family with kids":
        childcare_data = with_monthly_and_annual_labels(childcare_data_raw)
    else:
        childcare_data = {"No Childcare (N/A)": 0}  # single folk won't see a real cost

    ############################################################################
    # 5. User Selections
    ############################################################################
    st.subheader("Select Your Career")
    selected_career = st.selectbox("Career Path:", list(career_data.keys()))
    annual_salary = career_data[selected_career]

    st.subheader("Select Your Housing")
    selected_housing = st.selectbox("Housing Option:", list(housing_labeled.keys()))
    # fetch the raw key
    housing_key = housing_labeled[selected_housing]
    annual_housing_cost = housing_data_raw[housing_key][0]   # first element
    annual_home_insurance = housing_data_raw[housing_key][1] # second element

    st.subheader("Select Your Vehicle")
    selected_vehicle = st.selectbox("Vehicle Option:", list(vehicle_labeled.keys()))
    vehicle_key = vehicle_labeled[selected_vehicle]
    annual_vehicle_payment = vehicle_data_raw[vehicle_key][0]
    vehicle_mpg = vehicle_data_raw[vehicle_key][1]

    # Gas cost inputs
    if vehicle_key != "No Car (Public Transport)":
        st.subheader("Annual Driving Information")
        annual_miles = st.number_input("How many miles do you drive per year?", min_value=0, value=10000)
        gas_price = st.number_input("Average gas price per gallon?", min_value=0.0, value=3.50, format="%.2f")
        # Compute gas cost if user has a real vehicle
        if vehicle_mpg > 0:
            gallons_per_year = annual_miles / vehicle_mpg
            annual_gas_cost = gallons_per_year * gas_price
        else:
            annual_gas_cost = 0
    else:
        # No Car => no gas cost
        annual_miles = 0
        gas_price = 0
        annual_gas_cost = 0

    st.subheader("Select Your Groceries Budget")
    selected_groceries = st.selectbox("Groceries:", list(groceries_data.keys()))
    annual_groceries_cost = groceries_data[selected_groceries]

    st.subheader("Select Your Medical Insurance")
    selected_medical = st.selectbox("Medical Plan:", list(medical_data.keys()))
    annual_medical_cost = medical_data[selected_medical]

    # If family => childcare
    if family_status == "Family with kids":
        st.subheader("Childcare / Daycare")
        selected_childcare = st.selectbox("Childcare Option:", list(childcare_data.keys()))
        annual_childcare_cost = childcare_data[selected_childcare]
    else:
        annual_childcare_cost = 0

    st.subheader("Select Your Phone Plan")
    selected_phone = st.selectbox("Phone Plan:", list(phone_data.keys()))
    annual_phone_cost = phone_data[selected_phone]

    st.subheader("Select Your Utilities")
    selected_utilities = st.selectbox("Utilities:", list(utilities_data.keys()))
    annual_utilities_cost = utilities_data[selected_utilities]

    st.subheader("Select Your College Loan Repayment")
    selected_loan = st.selectbox("Loan Repayment:", list(loan_data.keys()))
    annual_loan_cost = loan_data[selected_loan]

    st.subheader("Select Your Entertainment")
    selected_entertainment = st.selectbox("Entertainment:", list(entertainment_data.keys()))
    annual_entertainment_cost = entertainment_data[selected_entertainment]

    st.subheader("Retirement Savings (as % of Salary)")
    selected_retirement = st.selectbox("Contribution:", list(retirement_data.keys()))
    retirement_fraction = retirement_data[selected_retirement]
    annual_retirement_cost = annual_salary * retirement_fraction

    ############################################################################
    # 6. Calculate Taxes & Discretionary Income
    ############################################################################
    tax_amount = compute_taxes(annual_salary)

    # Sum up all expenses
    total_expenses = (
        annual_housing_cost +
        annual_home_insurance +  # mandatory home/renters insurance
        annual_vehicle_payment +
        annual_gas_cost +
        annual_groceries_cost +
        annual_medical_cost +
        annual_childcare_cost +  # only > 0 if family
        annual_phone_cost +
        annual_utilities_cost +
        annual_loan_cost +
        annual_entertainment_cost +
        annual_retirement_cost
    )

    discretionary_income = annual_salary - tax_amount - total_expenses

    ############################################################################
    # 7. Display Summary
    ############################################################################
    st.write("---")
    st.write("## Summary of Your Choices & Costs (Annual)")

    st.write(f"- **Family Status**: {family_status}")
    st.write(f"- **Career**: {selected_career} => **${annual_salary:,.0f}**")
    st.write(f"- **Taxes**: **${tax_amount:,.0f}**")
    st.write(f"- **Housing**: {selected_housing} => **${annual_housing_cost:,.0f}** + home insurance **${annual_home_insurance:,.0f}**")
    st.write(f"- **Vehicle**: {selected_vehicle} => **${annual_vehicle_payment:,.0f}**")
    if vehicle_key != "No Car (Public Transport)":
        st.write(f"   - Annual Miles: **{annual_miles:,.0f}** at {vehicle_mpg} MPG, Gas = **${annual_gas_cost:,.0f}**")
    st.write(f"- **Groceries**: {selected_groceries} => **${annual_groceries_cost:,.0f}**")
    st.write(f"- **Medical**: {selected_medical} => **${annual_medical_cost:,.0f}**")

    if family_status == "Family with kids":
        st.write(f"- **Childcare**: => **${annual_childcare_cost:,.0f}**")
    st.write(f"- **Phone**: {selected_phone} => **${annual_phone_cost:,.0f}**")
    st.write(f"- **Utilities**: {selected_utilities} => **${annual_utilities_cost:,.0f}**")
    st.write(f"- **College Loan**: {selected_loan} => **${annual_loan_cost:,.0f}**")
    st.write(f"- **Entertainment**: {selected_entertainment} => **${annual_entertainment_cost:,.0f}**")
    st.write(f"- **Retirement**: {selected_retirement} => **${annual_retirement_cost:,.0f}**")

    if discretionary_income < 0:
        st.error(f"**Discretionary Income: -${abs(discretionary_income):,.0f}**")
    else:
        st.success(f"**Discretionary Income: ${discretionary_income:,.0f}**")

    ############################################################################
    # 8. Waterfall Chart WITHOUT Double Counting
    ############################################################################
    # We'll give the final "Discretionary Income" step an Amount=0, 
    # but label the bar with the leftover.

    data_steps = [
        {"Category": "Starting Salary",       "Amount": annual_salary},
        {"Category": "Taxes",                 "Amount": -tax_amount},
        {"Category": "Housing",               "Amount": -annual_housing_cost},
        {"Category": "Home Insurance",        "Amount": -annual_home_insurance},
        {"Category": "Vehicle Payment",       "Amount": -annual_vehicle_payment},
        {"Category": "Gas",                   "Amount": -annual_gas_cost},
        {"Category": "Groceries",             "Amount": -annual_groceries_cost},
        {"Category": "Medical Insurance",     "Amount": -annual_medical_cost},
        {"Category": "Childcare",             "Amount": -annual_childcare_cost},
        {"Category": "Phone Plan",            "Amount": -annual_phone_cost},
        {"Category": "Utilities",             "Amount": -annual_utilities_cost},
        {"Category": "College Loan",          "Amount": -annual_loan_cost},
        {"Category": "Entertainment",         "Amount": -annual_entertainment_cost},
        {"Category": "Retirement",            "Amount": -annual_retirement_cost},
        {"Category": "Discretionary Income",  "Amount": 0},
    ]

    df_steps = pd.DataFrame(data_steps)
    df_steps["Cumulative"] = df_steps["Amount"].cumsum()
    df_steps["Start"] = df_steps["Cumulative"].shift(1, fill_value=0)
    df_steps["End"] = df_steps["Cumulative"]

    # Custom label that shows the leftover on the final bar
    def get_label(row):
        if row["Category"] == "Discretionary Income":
            return discretionary_income
        else:
            return row["Cumulative"]

    df_steps["Label"] = df_steps.apply(get_label, axis=1)

    def pick_color(cat):
        if cat == "Starting Salary":
            return "green"
        elif cat == "Discretionary Income":
            return "blue" if discretionary_income >= 0 else "red"
        else:
            return "red"

    df_steps["Color"] = df_steps["Category"].apply(pick_color)

    base = alt.Chart(df_steps)

    bars = base.mark_bar().encode(
        x=alt.X("Category:N", sort=None, title=""),
        y=alt.Y("Start:Q", title="Annual Amount (USD)"),
        y2="End:Q",
        color=alt.Color("Color:N", scale=None),
        tooltip=[
            alt.Tooltip("Category:N",    title="Category"),
            alt.Tooltip("Amount:Q",      title="Step Amount", format=",.0f"),
            alt.Tooltip("Cumulative:Q",  title="Cumulative",  format=",.0f")
        ]
    )

    labels = base.mark_text(
        dy=-5,
        color="black",
        fontWeight="bold"
    ).encode(
        x=alt.X("Category:N", sort=None),
        y=alt.Y("End:Q"),
        text=alt.Text("Label:Q", format=",.0f")
    )

    waterfall_chart = (bars + labels).properties(
        width=800,
        height=400
    )

    st.write("---")
    st.write("## Waterfall Chart: Income to Discretionary Breakdown")
    st.altair_chart(waterfall_chart, use_container_width=True)

if __name__ == "__main__":
    main()
