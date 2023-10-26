<!-- ![Iberia Advisory](./Images/iberia-logo.png) -->

<img src="./Images/iberia-logo.png" width="600" height="300">

# Iberia Advisory Automation Tools

Welcome to the Iberia Advisory Automation Tools repository. This currently consists of two Python applications built using Streamlit, designed to automate data processing tasks. The applications included are:

1. **Tripwire Tracker App**: A tool for tracking and analyzing data from the Onboarding Tracker and Hourly Cost Excel files.

2. **Subcontractor Invoice Review App**: A tool for processing subcontractor labor invoice data and Consolidated WSR files.

## Table of Contents

- [App Overview](#App-overview)
- [Features](#features)
- [Prerequisites](#prerequisites)
- [Setup and Installation](#setup-and-installation)
- [Usage](#usage)

## App Overview

This app provides a central hub for Iberia Advisory's proprietary automation tools. Iberians can access and utilize these tools from a single location.

## Features

### Tripwire Tracker App

- Extracts relevant data from the Onboarding Tracker and Hourly Cost Excel files.
- Filters employees with 'Final Approval' in the Onboarding Tracker.
- Identifies employees above the 'Tripwire Rate' in the Hourly Cost file.
- Maps 'PLC Desc' to 'Correct LCAT Syntax' using Onboarding Tracker data.
- Presents processed data in a table format for analysis.

### Subcontractor Invoice Review App

- Processes labor invoice data and Consolidated WSR files.
- Allows users to input date ranges for contractors on the invoice.
- Calculates total hours, contract rates, and cost checks for contractors.
- Presents processed invoice data for review and analysis.

## Prerequisites

Before you begin, ensure you have met the following requirements:

- Python 3.x installed on your machine.
- The necessary Python libraries, including Streamlit, pandas, openpyxl, and pyxlsb, installed. You can install these libraries using pip.

## Setup and Installation

1. Clone this repository to your local machine:


       git clone https://github.com/RichieGarafola-IberiaAdvisory/

2. Change into the project directory:

        cd IberiaAdvisory
        
3. Install the required Python libraries:       
   
        pip install -r requirements.txt
        
## Usage

To run the applications, use the following commands:

1. For the Tripwire Tracker App:

        streamlit run tripwire_tracker.py

2. For the Subcontractor Invoice Review App:

        streamlit run subcontractor_invoice_review.py

Follow the on-screen instructions to use the applications.
