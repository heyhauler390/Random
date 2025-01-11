import streamlit as st
import pandas as pd
import altair as alt

def main():
    st.title("College Financial Decisions App")
    st.write(
        """
        This app helps illustrate how various financial decisions 
        can impact your end-of-year discretionary income. 
        Adjust the options below to see how much money you have left!
        """
    )

    # 1. Define data for the career paths (annual salary)
    career_data = {
        "Software Engineer": 90000,
        "Teacher": 45000,
        "Nurse": 65000,
        "Marketing Specialist": 55000,
        "Graphic Designer": 50000,
        "Data Scientist": 100000
    }

    # 2. Define data for the home choices (annual cost)
    home_data = {
        "Rent an Apartment": 12000,
        "Buy a Cheap House": 18000,
        "Buy a Nice House": 30000
    }

    # 3. Define data for the vehicle choices (annual cost)
    vehicle_data = {
        "No Car (Public Transport)": 2000,
        "Economy Car": 4000,
        "SUV": 6000,
        "Luxury Car": 10000
    }

    # 4. Define data for groceries (annual cost)
    grocery_data = {
        "Minimal Groceries": 2400,
        "Basic Groceries": 3600,
        "Premium Groceries": 6000
    }

    # 5. Define data for college loan repayments (annual cost)
    loan_data = {
        "No Loans": 0,
        "Low Repayment": 3000,
        "Medium Repayment": 6000,
        "High Repayment": 12000
    }

    # 6. Define data for utilities (annual cost)
    utilities_data = {
        "Low Utilities": 1800,
        "Medium Utilities": 3000,
        "High Utilities": 4800
    }

    # 7. Define data for insurance (annual cost)
    insurance_data = {
        "Basic Insurance": 1200,
        "Standard Insurance": 2400,
        "Comprehensive": 4800
    }

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
    total_expenses = (
        home_cost
        + vehicle_cost
        + grocery_cost
        + loan_cost
        + utilities_cost
        + insurance_cost
    )
    discretionary_income = annual_salary - total_expenses

    st.write("---")
    st.subheader("Summary of Your Choices")
    st.write(f"**Career Path:** {selected_career} - Annual Salary: ${annual_salary:,.0f}")
    st.write(f"**Home Choice:** {selected_home} - Annual Cost: ${home_cost:,.0f}")
    st.write(f"**Vehicle Choice:** {selected_vehicle} - Annual Cost: ${vehicle_cost:,.0f}")
    st.write(f"**Groceries:** {selected_groceries} - Annual Cost: ${grocery_cost:,.0f}")
    st.write(f"**College Loan:** {selected_loan} - Annual Cost: ${loan_cost:,.0f}")
    st.write(f"**Utilities:** {selected_utilities} - Annual Cost: ${utilities_cost:,.0f}")
    st.write(f"**Insurance:** {selected_insurance} - Annual Cost: ${insurance_cost:,.0f}")

    st.subheader("End-of-Year Discretionary Income")
    st.write(f"**${discretionary_income:,.0f}**")

    # --- Visualization: Bar Chart for Salary vs. Expenses ---
    st.write("### Visual Breakdown (Salary vs. Expenses)")
    data_bar = {
        'Item': ['Annual Salary', 'Total Expenses', 'Discretionary Income'],
        'Amount': [annual_salary, total_expenses, discretionary_income]
    }
    df_bar = pd.DataFrame(data_bar) 
    st.bar_chart(df_bar.set_index('Item'))

    # --- Sidebar Pie Chart: Expense Breakdown ---
    expenses_dict = {
        "Home": home_cost,
        "Vehicle": vehicle_cost,
        "Groceries": grocery_cost,
        "Loan Repayment": loan_cost,
        "Utilities": utilities_cost,
        "Insurance": insurance_cost,
    }

    pie_df = pd.DataFrame({
        "Category": list(expenses_dict.keys()),
        "Amount": list(expenses_dict.values())
    })

    # Create a "Label" column that combines category + dollar amount
    pie_df["Label"] = pie_df.apply(
        lambda row: f"{row['Category']} (${row['Amount']:,})", axis=1
    )

    # Main arc layer
    pie = (
        alt.Chart(pie_df)
        .mark_arc(outerRadius=80)
        .encode(
            theta=alt.Theta("Amount", stack=True),
            color=alt.Color("Category", legend=None),
            tooltip=["Category", "Amount"]
        )
    )

    # Text layer for labels
    # 'radius' controls how far the labels sit from the center.
    # Increase or decrease if you find they overlap or appear off-chart.
    text = (
        alt.Chart(pie_df)
        .mark_text(radius=110, size=10)
        .encode(
            theta=alt.Theta("Amount", stack=True),
            text=alt.Text("Label:N"),
            color=alt.value("black")  # text color
        )
    )

    # Layer the pie slices and the text
    pie_chart = alt.layer(pie, text).properties(
        title="Expense Breakdown",
        width=250,
        height=250
    )

    # Place the pie chart in the sidebar
    st.sidebar.header("Your Expense Breakdown")
    st.sidebar.altair_chart(pie_chart, use_container_width=True)

if __name__ == "__main__":
    main()
