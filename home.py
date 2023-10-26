import streamlit as st

# Set the title and page description
st.title("Welcome to IberiaAdvisory's Home")
st.markdown("This is the home for IberiaAdvisory's proprietary tools for automating tasks.")

# Home page content
st.write("Welcome to IberiaAdvisory's Home, the central hub for our exclusive tools designed to automate various processes.")

st.write("Explore the following sections to access our suite of powerful automation tools:")

# Section for Tool 1
st.header("Tool 1: Tripwire Tracker")
st.write("The Tripwire Tracker App is a Python script designed to process data from Excel files and filter information based on specific criteria.")
st.write("Key Features:")
st.write("- Extracts relevant data from the Onboarding Tracker and Hourly Cost Excel files.")
st.write("- Filters employees with 'Final Approval' in the Onboarding Tracker.")
st.write("- Identifies employees above the 'Tripwire Rate' in the Hourly Cost file.")
st.write("- Maps 'PLC Desc' to 'Correct LCAT Syntax' using Onboarding Tracker data.")
st.write("- Presents processed data in a table format for analysis.")

# Section for Tool 2
st.header("Tool 2: Subcontractor Invoice Review")
st.write("The Subcontractor Invoice Review App is a Python script designed to process data from Excel files and filter information based on specific criteria.")
st.write("Key Features:")
st.write("- Processes labor invoice data and Consolidated WSR files.")
st.write("- Allows users to input date ranges for contractors on the invoice.")
st.write("- Calculates total hours, contract rates, and cost checks for contractors.")
st.write("- Presents processed invoice data for review and analysis.")


st.markdown("---")
# Footer
st.write("If you have any questions or need assistance, please feel free to contact Richie RGarafola@IberiaAdvisory.com")
