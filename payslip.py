import streamlit as st
import datetime
from fpdf import FPDF
import base64
from io import BytesIO
import requests

def format_currency(amount):
    """Formats the amount with commas, without Naira sign."""
    return f"{amount:,.2f}"

def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add logo at top-right corner of the PDF
    logo_url = "https://raw.githubusercontent.com/petermartian/payslip_S9/main/Salmnine%20logo.png"
    try:
        response = requests.get(logo_url, stream=True)
        if response.status_code == 200:
            logo_img = BytesIO(response.content)
            # Place logo at top-right: A4 width is 210mm, logo width is 50mm, so x = 210 - 50 - margin
            pdf.image(logo_img, x=150, y=10, w=50)  # Adjust x, y, w as needed
        else:
            print(f"Failed to fetch logo for PDF. Status code: {response.status_code}")
            # Fallback: Add a placeholder text in the PDF if the logo fails to load
            pdf.set_xy(150, 10)
            pdf.set_text_color(255, 0, 0)  # Red text for error
            pdf.cell(0, 10, txt="Logo failed to load", align='R')
            pdf.set_text_color(0, 0, 0)  # Reset to black
    except Exception as e:
        print(f"Error loading logo for PDF: {str(e)}")
        # Fallback: Add a placeholder text in the PDF if the logo fails to load
        pdf.set_xy(150, 10)
        pdf.set_text_color(255, 0, 0)  # Red text for error
        pdf.cell(0, 10, txt="Logo failed to load", align='R')
        pdf.set_text_color(0, 0, 0)  # Reset to black

    # Colors for headers
    pdf.set_text_color(0, 0, 0)  # Black text for all headers

    # Header (shifted down to start below the logo)
    pdf.set_y(40)  # Adjust y-coordinate to start below the logo
    pdf.set_fill_color(255, 165, 0)  # Orange for "Payslip" header
    pdf.cell(0, 10, txt="Payslip", ln=True, align='C', border=1, fill=True)

    pdf.set_fill_color(0, 174, 239)  # Cyan Blue (matches logo) for Company Name
    pdf.cell(0, 10, txt=data["company_name"], ln=True, align='C', border=1, fill=True)

    pdf.set_fill_color(135, 206, 250)  # Sky Blue for Company Address
    pdf.cell(0, 10, txt=data["company_address"], ln=True, align='C', border=1, fill=True)
    pdf.ln(10)

    # Details
    pdf.set_fill_color(240, 248, 255)  # Alice Blue for regular cells
    pdf.cell(95, 10, txt=f"Pay Date: {data['pay_date']}", ln=False, border=1)
    pdf.set_font("Arial", 'B', size=12)  # Bold font
    pdf.cell(95, 10, txt=f"Employee Name: {data['employee_name']}", ln=True, border=1)
    pdf.set_font("Arial", size=12)  # Reset font
    pdf.cell(95, 10, txt=f"Working Days: {data['working_days']}", ln=False, border=1)
    pdf.set_font("Arial", 'B', size=12)  # Bold font
    pdf.cell(95, 10, txt=f"Employee ID: {data['employee_id']}", ln=True, border=1)
    pdf.set_font("Arial", size=12)  # Reset font
    pdf.ln(10)

    # Earnings & Deductions
    pdf.set_fill_color(255, 105, 180)  # Hot Pink for "Earnings" header
    pdf.cell(95, 10, txt="Earnings", ln=False, border=1, fill=True)
    pdf.set_fill_color(255, 99, 71)  # Tomato Red for "Deductions" header
    pdf.cell(90, 10, txt="Deductions", ln=True, border=1, fill=True)

    pdf.set_fill_color(240, 248, 255)  # Alice Blue for regular cells
    pdf.cell(95, 10, txt=f"Basic Pay: {format_currency(data['basic_pay'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Tax: {format_currency(data['tax'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Housing: {format_currency(data['Housing'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Pension (Employee): {format_currency(data['employee_pension'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Transport: {format_currency(data['Transport'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Other Deductions: {format_currency(data['other_deductions'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Other Allowances: {format_currency(data['other_allowances'])}", ln=False, border=1)
    pdf.ln(10)

    pdf.set_fill_color(144, 238, 144)  # Light Green for "Total Earnings"
    pdf.cell(95, 10, txt=f"Total Earnings: {format_currency(data['total_earnings'])}", ln=False, border=1, fill=True)
    pdf.set_fill_color(255, 182, 193)  # Light Pink for "Total Deductions"
    pdf.cell(90, 10, txt=f"Total Deductions: {format_currency(data['total_deductions'])}", ln=True, border=1, fill=True)

    pdf.set_fill_color(173, 216, 230)  # Light Blue for "Net Pay"
    pdf.cell(95, 10, txt=f"Net Pay: {format_currency(data['net_pay'])}", ln=False, border=1, fill=True)

    pdf_bytes = pdf.output(dest='S').encode('latin1')  # Default encoding
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    return pdf_base64

def main():
    st.title("S9 Payslip Generator")

    # Header Details
    st.header("Header Details")
    # Display logo in the UI
    logo_url = "https://raw.githubusercontent.com/petermartian/payslip_S9/main/Salmnine%20logo.png"
    try:
        response = requests.get(logo_url, stream=True)
        if response.status_code == 200:
            logo_img = BytesIO(response.content)
            st.image(logo_img, width=150)  # Adjust width as needed
        else:
            st.error(f"Failed to load logo. Status code: {response.status_code}")
    except Exception as e:
        st.error(f"Error loading logo: {str(e)}")

    company_name = st.text_input("Company Name", value="Salmnine Investment Ltd")
    company_address = st.text_input("Company Address", value="FF Millennium Towers, Ligali Ayorinde, Victoria Island, Lagos")

    # Payslip & Employee Details
    st.header("Employee Details")
    col1, col2 = st.columns(2)
    with col1:
        pay_date = st.date_input("Pay Date", datetime.date(2025, 4, 11))
        working_days = st.number_input("Working Days", value=31)
        st.button("Add Item (Pay Date/Working Days)")

    with col2:
        employee_name = st.text_input("Employee Name", value="James Arthur")
        employee_id = st.text_input("Employee ID", value="0077")
        st.button("Add Item (Employee Name/ID)")

    # Salary Details
    st.header("Salary Details")
    col3, col4 = st.columns(2)
    with col3:
        st.subheader("Earnings")
        basic_pay = st.number_input("Basic Pay", value=400000)
        Housing = st.number_input("Housing", value=200000)
        Transport = st.number_input("Transport", value=200000)
        other_allowances = st.number_input("Other Allowances", value=23000)
        total_earnings = basic_pay + Housing + Transport + other_allowances
        st.write(f"Total Earnings: {format_currency(total_earnings)}")

    with col4:
        st.subheader("Deductions")
        tax = st.number_input("Tax", value=100000)
        employee_pension = st.number_input("Pension (Employee)", value=57000)
        other_deductions = st.number_input("Other Deductions", value=0)
        total_deductions = tax + employee_pension + other_deductions
        st.write(f"Total Deductions: {format_currency(total_deductions)}")

    net_pay = total_earnings - total_deductions
    st.subheader("Net Pay")
    st.write(format_currency(net_pay))

    # PDF Download
    if st.button("Generate Payslip PDF"):
        data = {
            "company_name": company_name,
            "company_address": company_address,
            "pay_date": pay_date,
            "working_days": working_days,
            "employee_name": employee_name,
            "employee_id": employee_id,
            "basic_pay": basic_pay,
            "Housing": Housing,
            "Transport": Transport,
            "other_allowances": other_allowances,
            "total_earnings": total_earnings,
            "tax": tax,
            "employee_pension": employee_pension,
            "other_deductions": other_deductions,
            "total_deductions": total_deductions,
            "net_pay": net_pay,
        }
        pdf_base64 = generate_pdf(data)
        href = f'<a href="data:application/pdf;base64,{pdf_base64}" download="payslip.pdf">Download Payslip PDF</a>'
        st.markdown(href, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
