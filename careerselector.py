import streamlit as st
import pandas as pd
import altair as alt

# Helper function to build a new dictionary that shows both 
# the original name AND monthly cost in the label.
def with_monthly_labels(data_dict):
    """ 
    data_dict: { "Plain Label": annual_value, ... }
    returns: { "Plain Label ($X,XXX/mo)": annual_value, ... }
    """
    labeled_dict = {}
    for name, annual_cost in data_dict.items():
        monthly_cost = annual_cost / 12
        label = f"{name} (${monthly_cost:,.0f}/mo)"
        labeled_dict[label] = annual_cost
    return labeled_dict

def main():
    st.title("College Financial Decisions App (Waterfall Edition)")
    st.write(
        """
        This app helps illustrate how various financial decisions 
        reduce your overall annual salary, eventually showing your 
        end-of-year discretionary income. We also display monthly 
        costs in each selection for clarity.
        """
    )

    # 1. Define raw data for annual costs (or salaries).
    #    We'll convert them into labeled versions with monthly costs.
    career_data_raw = {
        "Software Engineer": 90000,
        "Teacher": 45000,
        "Nurse": 65000,
        "Marketing Specialist": 55000,
        "Graphic Designer": 50000,
        "Data Scientist": 100000
    }
    home_data_raw = {
        "Rent an Apartment": 12000,
        "Buy a Cheap House": 18000,
        "Buy a Nice House": 30000
    }
    vehicle_data_raw = {
        "No Car (Public Transport)": 2000,
        "Economy Car": 4000,
        "SUV": 6000,
        "Luxury Car": 10000
    }
    grocery_data_raw = {
        "Minimal Groceries": 2400,
        "Basic Groceries": 3600,
        "Premium Groceries": 6000
    }
    loan_data_raw = {
        "No Loans": 0,
        "Low Repayment": 3000,
        "Medium Repayment": 6000,
        "High Repayment": 12000
    }
    utilities_data_raw = {
        "Low Utilities": 1800,
        "Medium Utilities": 3000,
        "High Utilities": 4800
    }
    insurance_data_raw = {
        "Basic Insurance": 1200,
        "Standard Insurance": 2400,
        "Comprehensive": 4800
    }

    # 2. Convert each dictionary to a "labeled" version showing monthly cost.
    career_data = with_monthly_labels(career_data_raw)
    home_data = with_monthly_labels(home_data_raw)
    vehicle_data = with_monthly_labels(vehicle_data_raw)
    grocery_data = with_monthly_labels(grocery_data_raw)
    loan_data = with_monthly_labels(loan_data_raw)
    utilities_data = with_monthly_labels(utilities_data_raw)
    insurance_data = with_monthly_labels(insurance_data_raw)

    # --- Career Path ---
    st.subheader("1. Choose a Career")
    selected_career = st.selectbox("Select your career path:", list(career_data.keys()))
    annual_salary = career_data[selected_career]

    # --- Home Decision ---
    st.subheader("2. Home Decision")
    selected_home = st.selectbox("Select a home option:", list(home_data.keys()))
    home_cost = home_data[selected_home]

    # --- Vehicle Decision ---
    st.subheader("3. Vehicle Decision")
    selected_vehicle = st.selectbox("Select a vehicle option:", list(vehicle_data.keys()))
    vehicle_cost = vehicle_data[selected_vehicle]

    # --- Groceries ---
    st.subheader("4. Groceries Budget")
    selected_groceries = st.selectbox("Select your grocery spending:", list(grocery_data.keys()))
    grocery_cost = grocery_data[selected_groceries]

    # --- College Loan ---
    st.subheader("5. College Loan Repayment")
    selected_loan = st.selectbox("Select your loan repayment:", list(loan_data.keys()))
    loan_cost = loan_data[selected_loan]

    # --- Utilities ---
    st.subheader("6. Utilities")
    selected_utilities = st.selectbox("Select your utilities budget:", list(utilities_data.keys()))
    utilities_cost = utilities_data[selected_utilities]

    # --- Insurance ---
    st.subheader("7. Insurance")
    selected_insurance = st.selectbox("Select your insurance level:", list(insurance_data.keys()))
    insurance_cost = insurance_data[selected_insurance]

    # --- Calculate Discretionary Income ---
    total_expenses = sum([
        home_cost,
        vehicle_cost,
        grocery_cost,
        loan_cost,
        utilities_cost,
        insurance_cost
    ])
    discretionary_income = annual_salary - total_expenses

    st.write("---")
    st.subheader("Summary of Your Choices")
    st.write(f"**Career Path:** {selected_career} => Annual Salary: ${annual_salary:,.0f}")
    st.write(f"**Home Choice:** {selected_home} => Annual Cost: ${home_cost:,.0f}")
    st.write(f"**Vehicle Choice:** {selected_vehicle} => Annual Cost: ${vehicle_cost:,.0f}")
    st.write(f"**Groceries:** {selected_groceries} => Annual Cost: ${grocery_cost:,.0f}")
    st.write(f"**College Loan:** {selected_loan} => Annual Cost: ${loan_cost:,.0f}")
    st.write(f"**Utilities:** {selected_utilities} => Annual Cost: ${utilities_cost:,.0f}")
    st.write(f"**Insurance:** {selected_insurance} => Annual Cost: ${insurance_cost:,.0f}")

    st.subheader("End-of-Year Discretionary Income")
    # If it can go negative, let's highlight that in red or just display it:
    if discretionary_income < 0:
        st.error(f"**Your discretionary income is: -${abs(discretionary_income):,.0f}** (negative!)")
    else:
        st.success(f"**${discretionary_income:,.0f}**")

    # --- Waterfall Chart with Altair ---
    st.write("### Waterfall Chart: Where Does Your Money Go?")

    # We'll construct a small DataFrame that shows each 'step':
    #  1. Starting Salary
    #  2. Subtract each expense
    #  3. Final leftover (discretionary income)
    # Each expense is negative, while the starting salary is positive.

    data_steps = [
        {"Category": "Starting Salary", "Amount": annual_salary},
        {"Category": "Home", "Amount": -home_cost},
        {"Category": "Vehicle", "Amount": -vehicle_cost},
        {"Category": "Groceries", "Amount": -grocery_cost},
        {"Category": "College Loan", "Amount": -loan_cost},
        {"Category": "Utilities", "Amount": -utilities_cost},
        {"Category": "Insurance", "Amount": -insurance_cost},
        {"Category": "Discretionary Income", "Amount": discretionary_income},
    ]

    df_steps = pd.DataFrame(data_steps)

    # We’ll create columns to compute the "cumulative" position of each step,
    # which is how a typical waterfall chart is built.
    df_steps["Cumulative"] = df_steps["Amount"].cumsum()

    # We'll also define columns for the range of each bar.
    # - The "start" of each bar is the previous cumulative (shift down by 1).
    # - The "end" is the current cumulative.
    df_steps["Start"] = df_steps["Cumulative"].shift(1, fill_value=0)
    df_steps["End"] = df_steps["Cumulative"]

    # For color encoding, let's label positive steps (the salary, discretionary) 
    # vs negative steps (the expenses).
    def bar_color(cat, amt):
        if cat == "Starting Salary":
            return "green"
        elif cat == "Discretionary Income":
            return "blue" if amt >= 0 else "red"
        else:
            # Everything else is an expense
            return "red"

    df_steps["Color"] = df_steps.apply(lambda row: bar_color(row["Category"], row["Amount"]), axis=1)

    # We'll create a layered Altair chart:
    # - A rule for the baseline
    # - A bar for each step
    # - Labels to show the amounts
    base = alt.Chart(df_steps)

    bars = base.mark_bar().encode(
        x=alt.X("Category:N", sort=None, title=""),
        y=alt.Y("Start:Q", title="Annual Amount (USD)"),
        y2="End:Q",
        color=alt.Color("Color:N", scale=None),  # we specify exact color in data
        tooltip=[
            alt.Tooltip("Category:N", title="Category"),
            alt.Tooltip("Amount:Q", title="Step Amount", format=",.0f"),
            alt.Tooltip("Cumulative:Q", title="Cumulative", format=",.0f")
        ]
    )

    # For label text, we can place it at the midpoint of each bar
    labels = base.mark_text(
        dy=-5,  # shift text upward
        color="black",
        fontWeight="bold"
    ).encode(
        x=alt.X("Category:N", sort=None),
        y=alt.Y("End:Q"),
        text=alt.Text("Cumulative:Q", format=",.0f")
    )

    # Combine them:
    waterfall_chart = (bars + labels).properties(
        width=600,
        height=400
    )

    st.altair_chart(waterfall_chart, use_container_width=True)

    # --- Sidebar Pie (Optional) ---
    # If you still want a pie breakdown, you can place it in the sidebar:
    st.sidebar.header("Expense Breakdown")
    expense_items = {
        "Home": home_cost,
        "Vehicle": vehicle_cost,
        "Groceries": grocery_cost,
        "College Loan": loan_cost,
        "Utilities": utilities_cost,
        "Insurance": insurance_cost,
    }
    pie_df = pd.DataFrame({
        "Category": expense_items.keys(),
        "Amount": expense_items.values()
    })
    pie_chart = alt.Chart(pie_df).mark_arc(outerRadius=70).encode(
        theta=alt.Theta("Amount", stack=True),
        color=alt.Color("Category", legend=None),
        tooltip=["Category", "Amount"]
    )
    st.sidebar.altair_chart(pie_chart, use_container_width=True)

if __name__ == "__main__":
    main()
