import os
import pandas as pd
import streamlit as st
from openpyxl import Workbook
import base64
from io import BytesIO
from datetime import datetime, timedelta

import matplotlib.pyplot as plt
import seaborn as sns

# Set the page configuration for the Streamlit application, including the title and icon.
st.set_page_config(
    page_title="Iberia Advisory Tripewire Tracker",
    page_icon="📊",
    layout="wide"
)

# Display the Iberia Advisory image on the Streamlit application.
st.image("./Images/iberia-logo.png")

################
# AUTHENICATION
################

# Define a function check_password() that handles user authentication.
def check_password():
    """Returns `True` if the user had a correct password."""

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if (
            st.session_state["username"] in st.secrets["passwords"]
            and st.session_state["password"]
            == st.secrets["passwords"][st.session_state["username"]]
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # don't store username + password
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # First run, show inputs for username + password.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        return False
    elif not st.session_state["password_correct"]:
        # Password not correct, show input + error.
        st.text_input("Username", on_change=password_entered, key="username")
        st.text_input(
            "Password", type="password", on_change=password_entered, key="password"
        )
        st.error("😕 User not known or password incorrect")
        return False
    else:
        # Password correct.
        return True
    
# Check the user password using the check_password() function and sets the is_logged_in flag to True if the password is correct.
if check_password():
    is_logged_in = True
    
    start_time = datetime.now()

    # Function that allows you to find where the header is located within an Excel sheet
    @st.cache_data()
    def find_start_row(file_path, column_name, sheet_name=None):
        """
        Find the starting row index containing a specific column name in an Excel sheet.

        Parameters:
        - file_path (str): The file path of the Excel file to be searched.
        - column_name (str): The name of the column to search for within the sheet.
        - sheet_name (str, optional): The name of the sheet in the Excel file (default is None).
            If sheet_name is not provided, the function attempts to read the first sheet.

        Returns:
        - int: The row index where the specified column name is found.

        Raises:
        - ValueError: If the specified column name is not found in the sheet.

        This function reads the Excel file specified by 'file_path' and searches for the
        row containing the 'column_name' in the specified 'sheet_name' (or the first sheet if
        'sheet_name' is not provided). Once the row is found, the function returns its index.

        If the column name is not found in the sheet, a ValueError is raised.

        Example usage:
        start_row = find_start_row("example.xlsx", "Name", "Sheet1")
        """
        if sheet_name is None:
            # If sheet_name is not provided, try to read the first sheet
            df = pd.read_excel(file_path, header=None, index_col=None)
        else:
            df = pd.read_excel(file_path, header=None, index_col=None, sheet_name=sheet_name)

        for row_number, row in df.iterrows():
            if column_name in row.values:
                return row_number

        raise ValueError(f'Column "{column_name}" not found in the sheet "{sheet_name}" of the file.')

    # Function to generate histogram visualization
    @st.cache_resource()
    def generate_histogram(data):
        fig_histogram, ax_histogram = plt.subplots()
        sns.histplot(data["Hourly Cost $/hr"], bins=20, kde=True, ax=ax_histogram)
        ax_histogram.set_title("Hourly Cost Distribution")
        ax_histogram.set_xlabel("Hourly Cost $/hr")
        ax_histogram.set_ylabel("Count")
        st.pyplot(fig_histogram)

    # Function to generate box plot visualization
    @st.cache_resource()
    def generate_box_plot(data):
        fig_box_plot, ax_box_plot = plt.subplots()
        sns.boxplot(x="Above Tripwire Rate?", y="Hourly Cost $/hr", data=data, ax=ax_box_plot)
        ax_box_plot.set_title("Hourly Cost Distribution for Employees Above Tripwire Rate")
        ax_box_plot.set_xlabel("Above Tripwire Rate")
        ax_box_plot.set_ylabel("Hourly Cost $/hr")
        st.pyplot(fig_box_plot)

    # Function to generate pair plot visualization
    @st.cache_resource()
    def generate_pair_plot(data):
        fig_pair_plot = sns.pairplot(data, hue="Above Tripwire Rate?")
        fig_pair_plot.fig.suptitle("Hourly Cost Relationships", y=1.02)
        st.pyplot(fig_pair_plot)

    # Function to generate pie chart visualization
    @st.cache_resource()
    def generate_pie_chart(data):
        fig_pie_chart, ax_pie_chart = plt.subplots()
        data["Above Tripwire Rate?"].value_counts().plot.pie(autopct='%1.1f%%', ax=ax_pie_chart)
        ax_pie_chart.set_title("Proportion of Employees Above Tripwire Rate")
        st.pyplot(fig_pie_chart)

    # Function to generate box plot for hourly cost distribution by correct LCAT syntax
    @st.cache_resource()
    def generate_box_plot_lcat(data):
        fig_box_plot_lcat, ax_box_plot_lcat = plt.subplots(figsize=(12, 6))
        sns.boxplot(x="Correct LCAT Syntax", y="Hourly Cost $/hr", data=data, ax=ax_box_plot_lcat)
        ax_box_plot_lcat.set_xticklabels(ax_box_plot_lcat.get_xticklabels(), rotation=45, ha="right")
        ax_box_plot_lcat.set_title("Hourly Cost Distribution by Correct LCAT Syntax")
        st.pyplot(fig_box_plot_lcat)


    # Streamlit UI
    st.title('Tripwire Tracker App')

    # Sidebar instructions
    if st.sidebar.checkbox("Show Instructions"):
        st.write("This application is a tool for tracking and analyzing data from the Onboarding Tracker and Hourly Cost Excel files.")
        st.write("The Onboarding Tracker file can be found in the following subdirectory 'Restored FMO1', 'Onboarding', select the latest tracker file.")
        st.write("The Hourly Cost data will be emailed.")
        st.write("Upload the two Excel files Onboarding Tracker and the Hourly Cost file.")
        st.write("Use the 'Upload Onboarding Tracker Excel File' and 'Upload Hourly Cost Excel File' buttons to upload these files respectively.")
        st.write("Make sure the Hourly Cost file has the specific sheet name you want to work with.")
        st.write("Typically the sheet name is 'Hourly Cost_TO29OY1_BVN00XX'; however, this should be checked prior to running to ensure the file is read in correctly.")

        st.write("After uploading the files, the application processes the data. It performs the following tasks:")
        st.write("- Extracts relevant columns from both files.")
        st.write("- Normalizes Candidate Names by removing middle initials.")
        st.write("- Filters employees who have 'Final Approval' in the Onboarding Tracker.")
        st.write("- Determines which employees are above the 'Tripwire Rate' in the Hourly Cost file.")
        st.write("- Maps 'PLC Desc' to 'Correct LCAT Syntax' using data from the Onboarding Tracker.")
        st.write("Finally, it presents a DataFrame with processed data in a table format under the 'Processed Data' section.")

        st.write("If you want to save the processed data to an Excel file, you can:")
        st.write("- Enter a name for the Excel file in the 'Enter Excel File Name (without extension)' text field.")
        st.write("- Click the 'Save Data to Excel' button.")
        st.write("This will generate a download link for the Excel file. Click on the link to download the processed data.")
        st.write("The file will be saved to the Downloads folder by default.")

    # Upload Onboarding Tracker Excel file
    tracker_file = st.file_uploader("Upload Onboarding Tracker Excel File", type=["xlsx"])
    hourly_cost_file = st.file_uploader("Upload Hourly Cost Excel File", type=["xlsx"])

    # Specify the Hourly Cost sheet name for the provided file
    hourly_cost_sheet_name = st.text_input("Enter Hourly Cost Sheet Name:")

    # Specify the Tripwire Tracker sheet name in the Onboarding Tracker
    tracker_sheet_name = 'Tripwire Tracker'

    # Initialize the flag to indicate whether data is loaded
    data_loaded = False

    if tracker_file is not None and hourly_cost_file is not None:
        # Check if the user has provided a sheet name for hourly_cost_df
        if not hourly_cost_sheet_name:
            st.warning("Please enter the sheet name for the Hourly Cost Excel file.")
        else:
            # Use the find_start_row function to find the header row containing the desired column names
            tracker_header_row_index = find_start_row(tracker_file, "Candidate Name", tracker_sheet_name)

            # Read the Excel file into a Pandas DataFrame
            tracker_df = pd.read_excel(tracker_file, sheet_name=tracker_sheet_name, header=tracker_header_row_index)

            # Use the find_start_row function to find the header row containing the desired column names
            hourly_cost_header_row_index = find_start_row(hourly_cost_file, "Name", hourly_cost_sheet_name)

            # Read the Excel file into a Pandas DataFrame, specifying the header row index
            hourly_cost_df = pd.read_excel(hourly_cost_file, sheet_name=hourly_cost_sheet_name, header=hourly_cost_header_row_index)

            try:
                tracker_df.reset_index(drop=True, inplace=True)
                tracker_df = tracker_df[["Candidate Name", "Final Approval"]]

                hourly_cost_df.reset_index(drop=True, inplace=True)
                hourly_cost_df = hourly_cost_df[["Name", "PLC Desc", "Hourly Cost $/hr", "Above Tripwire Rate?"]]

                # Convert the "Hourly Cost $/hr" column to numeric (if it's not already)
                hourly_cost_df["Hourly Cost $/hr"] = pd.to_numeric(hourly_cost_df["Hourly Cost $/hr"], errors="coerce")

                # Round the "Hourly Cost $/hr" column to two decimal places
                hourly_cost_df["Hourly Cost $/hr"] = hourly_cost_df["Hourly Cost $/hr"].round(2)

                # Read LCAT Normalization data from Onboarding Tracker
                lcat_df = pd.read_excel(tracker_file, sheet_name='LCAT Normalization')
                lcat_df = lcat_df[["Vendor LCATs", "Correct LCAT Syntax"]]

                # Remove middle initials from names in both DataFrames
                tracker_df["Candidate Name"] = tracker_df["Candidate Name"].str.replace(r' [A-Z]\b', '', regex=True)
                hourly_cost_df["Name"] = hourly_cost_df["Name"].str.replace(r' [A-Z]\b', '', regex=True)

                # Filter Data
                filtered_tripwire_df = tracker_df[tracker_df["Final Approval"] == "Y"]
                names_above_tripwire = hourly_cost_df[hourly_cost_df["Above Tripwire Rate?"] == "Yes"]["Name"]
                names_allow_exceed_tripwire = filtered_tripwire_df[
                    filtered_tripwire_df["Final Approval"] == "Y"]["Candidate Name"]
                names_not_in_tripwire = names_above_tripwire[~names_above_tripwire.isin(names_allow_exceed_tripwire)]

                # Remove newline characters from the "PLC Desc" column in hourly_cost_df
                hourly_cost_df["PLC Desc"] = hourly_cost_df["PLC Desc"].str.strip()

                # Create a dictionary to map "Vendor LCATs" to "Correct LCAT Syntax"
                lcat_mapping = lcat_df.set_index("Vendor LCATs")["Correct LCAT Syntax"].to_dict()

                # Map the "PLC Desc" column in hourly_cost_df to get corrected LCAT syntax
                hourly_cost_df["Correct LCAT Syntax"] = hourly_cost_df["PLC Desc"].map(lcat_mapping)

                # Filter again
                filtered_hourly_cost_df = hourly_cost_df[hourly_cost_df["Name"].isin(names_not_in_tripwire)]

                # Output
                result_df = filtered_hourly_cost_df[["Name", "PLC Desc", "Correct LCAT Syntax", "Hourly Cost $/hr", "Above Tripwire Rate?"]]

                # Display the resulting DataFrame
                st.subheader("Processed Data")
                st.dataframe(result_df)

                # Set the flag to indicate that the data is loaded
                data_loaded = True

            except KeyError as e:
                # Inform the user to check if any tripwires are flagged
                st.error(f"Please check if any tripwires are flagged in the excel files.")              

        # Input field for Excel file name
        excel_filename = st.text_input("Enter Excel File Name (without extension)", "filtered_hourly_cost")

        # Save to Excel button
        if st.button('Save Data to Excel'):
            # Save the filtered dataframe to an Excel file in memory
            excel_buffer = BytesIO()
            result_df.to_excel(excel_buffer, index=False)
            excel_data = excel_buffer.getvalue()

            # Generate a download link for the Excel file
            b64 = base64.b64encode(excel_data).decode('utf-8')
            excel_filename = f"{excel_filename}.xlsx"
            href = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64}" download="{excel_filename}">Download Excel File</a>'
            st.markdown(href, unsafe_allow_html=True)

    #     end_time = datetime.now()
    #     elapsed_time = end_time - start_time

    #     st.write(f"Elapsed Time: {elapsed_time}")


    # Visualization Selection
    visualization_options = [
        "Histogram: Hourly Cost Distribution",
        "Box Plot: Hourly Cost Distribution for Employees", # Above Tripwire Rate",
        # "Pair Plot: Pairwise Relationships",
        "Pie Chart: Proportion of Employees Above Tripwire Rate",
        "Box Plot: Hourly Cost Distribution by Correct LCAT Syntax"
    ]

    selected_visualization = st.sidebar.selectbox("Select Visualization", visualization_options)

    # Display selected visualization only if data is loaded
    if data_loaded:
        col1, col2 = st.columns(2)
        with col1:
            if selected_visualization == "Histogram: Hourly Cost Distribution":
                generate_histogram(result_df)
            elif selected_visualization == "Box Plot: Hourly Cost Distribution for Employees":# Above Tripwire Rate":
                generate_box_plot(hourly_cost_df)
            # elif selected_visualization == "Pair Plot: Hourly Cost Relationships":
            #     generate_pair_plot(result_df)
            #     # generate_pair_plot(hourly_cost_df)
            elif selected_visualization == "Pie Chart: Proportion of Employees Above Tripwire Rate":
                generate_pie_chart(hourly_cost_df)
            elif selected_visualization == "Box Plot: Hourly Cost Distribution by Correct LCAT Syntax":
                generate_box_plot_lcat(hourly_cost_df)

    end_time = datetime.now()
    elapsed_time = end_time - start_time

    st.write(f"Elapsed Time: {elapsed_time}")
