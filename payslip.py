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
    pdf = FPDF()  # Removed encoding='utf-8'
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Add letterhead
    try:
        letterhead_url = "https://salmnine.com/wp-content/uploads/2024/08/letterhead.png"  # Replace with actual URL if needed
        response = requests.get(letterhead_url)
        letterhead_img = BytesIO(response.content)
        pdf.image(letterhead_img, x=0, y=0, w=210)  # Span the A4 page width
    except Exception as e:
        print(f"Error loading letterhead: {e}")

    # Add logo at top-right corner
    try:
        logo_url = "https://raw.githubusercontent.com/petermartian/payslip_S9/main/Salmnine%20logo.png"
        response = requests.get(logo_url)
        logo_img = BytesIO(response.content)
        # Place logo at top-right: A4 width is 210mm, logo width is 50mm, so x = 210 - 50 - margin
        pdf.image(logo_img, x=150, y=10, w=50)  # Adjust x, y, w as needed
    except Exception as e:
        print(f"Error loading logo: {e}")

    # Colors
    pdf.set_fill_color(240, 248, 255)  # Alice Blue
    pdf.set_text_color(0, 0, 0)  # Black

    # Header (shifted down to start below the letterhead and logo)
    pdf.set_y(70)  # Adjust y-coordinate to start below the letterhead and logo
    pdf.cell(0, 10, txt="Payslip", ln=True, align='C', border=1, fill=True)
    pdf.set_fill_color(173, 216, 230)  # Light Blue for Company Name
    pdf.cell(0, 10, txt=data["company_name"], ln=True, align='C', border=1, fill=True)
    pdf.set_fill_color(240, 248, 255)  # Reset to Alice Blue
    pdf.cell(0, 10, txt=data["company_address"], ln=True, align='C', border=1, fill=True)
    pdf.ln(10)

    # Details
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
    pdf.set_fill_color(220, 220, 220)  # Light Gray
    pdf.cell(95, 10, txt="Earnings", ln=False, border=1, fill=True)
    pdf.cell(90, 10, txt="Deductions", ln=True, border=1, fill=True)

    pdf.cell(95, 10, txt=f"Basic Pay: {format_currency(data['basic_pay'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Tax: {format_currency(data['tax'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Housing: {format_currency(data['Housing'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Pension (Employee): {format_currency(data['employee_pension'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Transport: {format_currency(data['Transport'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Other Deductions: {format_currency(data['other_deductions'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Other Allowances: {format_currency(data['other_allowances'])}", ln=False, border=1)
    pdf.ln(10)

    pdf.set_fill
