import os
import pandas as pd
from flask import Flask, render_template, request, redirect, url_for, send_file
from openpyxl import Workbook
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import qrcode
from io import BytesIO
import datetime

app = Flask(__name__)

import datetime
from flask import render_template

@app.route('/')
def index():
    success_message = request.args.get('success')
    return render_template('index.html', success=success_message, datetime=datetime)


# Global variables
ticket_number = 1
excel_file = "tickets.xlsx"

# Create a new Excel file if it doesn't exist
def create_excel_file():
    if not os.path.exists(excel_file):  # Check if the file exists
        wb = Workbook()
        sheet = wb.active
        sheet.append(['Ticket Number', 'Date', 'Time', 'Customer Name', 'Address', 'Relation', 'Phone Number', 'Amount', 'Receiver'])
        wb.save(excel_file)

# # Save ticket data to Excel
# @app.route('/save_ticket', methods=['POST'])
# def save_ticket():
#     global ticket_number
#     date = request.form['date']
#     time = request.form['time']
#     customer_name = request.form['customer_name']
#     address = request.form['address']
#     relation = request.form['relation']
#     phone_number = request.form['phone_number']
#     amount = request.form['amount']
#     receiver = request.form['receiver']

#     # Load existing data or create the file if it doesn't exist
#     create_excel_file()  # Ensure the file exists before reading it

#     # Load the data into a DataFrame
#     df = pd.read_excel(excel_file)

#     # Create a new DataFrame with the new ticket data
#     new_ticket = pd.DataFrame([{
#         'Ticket Number': ticket_number,
#         'Date': date,
#         'Time': time,
#         'Customer Name': customer_name,
#         'Address': address,
#         'Relation': relation,
#         'Phone Number': phone_number,
#         'Amount': amount,
#         'Receiver': receiver
#     }])

#     # Concatenate the new ticket data with the existing DataFrame
#     df = pd.concat([df, new_ticket], ignore_index=True)

#     # Save the updated DataFrame back to the Excel file
#     df.to_excel(excel_file, index=False)

#     # Increment ticket number
#     ticket_number += 1

#     return redirect(url_for('index', success="Ticket saved successfully!"))


# ---------------------------------------------------------------------

# Determine the starting ticket number
def get_starting_ticket_number():
    if os.path.exists(excel_file):  # Check if the Excel file exists
        df = pd.read_excel(excel_file)
        if 'Ticket Number' in df.columns and not df.empty:
            return df['Ticket Number'].max() + 1  # Start from the next number
    return 1  # Default to 1 if the file is empty or does not exist

# Save ticket data to Excel
@app.route('/save_ticket', methods=['POST'])
def save_ticket():
    global ticket_number
    # Update the ticket number based on existing data
    ticket_number = get_starting_ticket_number()

    date = request.form['date']
    time = request.form['time']
    customer_name = request.form['customer_name']
    address = request.form['address']
    relation = request.form['relation']
    phone_number = request.form['phone_number']
    amount = request.form['amount']
    receiver = request.form['receiver']

    # Load existing data or create the file if it doesn't exist
    create_excel_file()  # Ensure the file exists before reading it

    # Load the data into a DataFrame
    df = pd.read_excel(excel_file)

    # Create a new DataFrame with the new ticket data
    new_ticket = pd.DataFrame([{
        'Ticket Number': ticket_number,
        'Date': date,
        'Time': time,
        'Customer Name': customer_name,
        'Address': address,
        'Relation': relation,
        'Phone Number': phone_number,
        'Amount': amount,
        'Receiver': receiver
    }])

    # Concatenate the new ticket data with the existing DataFrame
    df = pd.concat([df, new_ticket], ignore_index=True)

    # Save the updated DataFrame back to the Excel file
    df.to_excel(excel_file, index=False)

    # Increment ticket number
    ticket_number += 1

    return redirect(url_for('index', success="Ticket saved successfully!"))

# ====================================================================
# @app.route('/search')
# def search():
#     return render_template('search.html')

# ------------------------------------------------------------------

@app.route('/search')
def search():
    return render_template('search.html', ticket_data=None, datetime=datetime)

@app.route('/search_ticket', methods=['GET', 'POST'])
def search_ticket():
    ticket_data = None  # Initialize as None for GET requests or when no results are found
    if request.method == 'POST':
        # Get the ticket number entered by the user
        ticket_number_to_search = request.form['ticket_number']

        # Load the Excel data into a DataFrame
        try:
            df = pd.read_excel(excel_file)

            # Filter the DataFrame for the entered ticket number
            ticket_data = df[df['Ticket Number'] == int(ticket_number_to_search)]

            # If no matching data is found, set ticket_data to None
            if ticket_data.empty:
                ticket_data = None

        except Exception as e:
            print(f"Error reading or processing the Excel file: {e}")
            ticket_data = None  # In case of error, pass None to the template

    return render_template('search.html', ticket_data=ticket_data, datetime=datetime)

# ----------------------------------------------------------------

# -----------------------------------------------------------------

# Summary Report
@app.route('/generate_summary_report', methods=['POST'])
def generate_summary_report():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    receiver_filter = request.form['receiver_filter']

    # Filter data
    df = pd.read_excel(excel_file)
    df['Date'] = pd.to_datetime(df['Date'])
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if receiver_filter != "All":
        filtered_df = filtered_df[filtered_df['Receiver'] == receiver_filter]

    # Generate summary
    total_entries = len(filtered_df)
    total_amount = filtered_df['Amount'].sum()
    max_amount = filtered_df['Amount'].max()
    min_amount = filtered_df['Amount'].min()

    summary_info = {
        'total_entries': total_entries,
        'total_amount': total_amount,
        'max_amount': max_amount,
        'min_amount': min_amount
    }

    return render_template('summary_report.html', summary_info=summary_info)

# Detailed Report
@app.route('/generate_detailed_report', methods=['POST'])
def generate_detailed_report():
    start_date = request.form['start_date']
    end_date = request.form['end_date']
    receiver_filter = request.form['receiver_filter']

    # Filter data
    df = pd.read_excel(excel_file)
    df['Date'] = pd.to_datetime(df['Date'])
    filtered_df = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if receiver_filter != "All":
        filtered_df = filtered_df[filtered_df['Receiver'] == receiver_filter]

    return render_template('detailed_report.html', report_data=filtered_df)

# Home page
# @app.route('/')
# def index():
#     success_message = request.args.get('success')
#     return render_template('index.html', success=success_message)

# @app.route('/version')
# def version():
#     version_file = "version.txt"
#     versions = []

#     if os.path.exists(version_file):
#         with open(version_file, 'r') as file:
#             content = file.read().strip()

#             # Split content by version headings and add them to the list
#             version_sections = content.split('version')
#             for section in version_sections:
#                 if section.strip():
#                     # Get version number and description
#                     version_details = section.strip().split("\n", 1)
#                     if len(version_details) > 1:
#                         version_number = version_details[0].strip()
#                         description = version_details[1].strip()
#                         versions.append({'version': version_number, 'description': description})

#     return render_template('version.html', versions=versions)


@app.route('/version')
def version():
    version_file = "version.txt"
    versions = []

    # Check if the version.txt file exists
    if os.path.exists(version_file):
        with open(version_file, 'r') as file:
            content = file.read().strip()
            
            # Print the content to the console for debugging
            print("Version file content:\n", content)

            # Split content by 'version' keyword
            version_sections = content.split('version')
            print("Version sections after splitting:\n", version_sections)  # Debugging the split
            
            for section in version_sections:
                if section.strip():
                    # Get version number and description
                    version_details = section.strip().split("\n", 1)
                    if len(version_details) > 1:
                        version_number = version_details[0].strip()
                        description = version_details[1].strip()
                        versions.append({'version': version_number, 'description': description})

    else:
        print("Version file does not exist.")

    # Check if the versions list has data and return to template
    if versions:
        return render_template('version.html', versions=versions)
    else:
        print("No versions found to display.")
        return render_template('version.html', versions=[])


# ===========================================================================

if __name__ == '__main__':
    app.run(debug=True, port=5001)
