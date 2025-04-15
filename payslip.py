import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
import base64
from io import BytesIO
import requests
import smtplib
from email.message import EmailMessage

# --- CONFIG ---
SENDER_EMAIL = "petmartian@gmail.com"
SENDER_PASSWORD = "salarypayslip1"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- PDF UTILS ---
def format_currency(amount):
    return f"{amount:,.2f}"

def generate_pdf(data, uploaded_logo=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    logo_url = "https://drive.google.com/file/d/1melsj54pPwsjmYGRE1SQg7EBLZ6BthCn/view?usp=drive_link"
    logo_added = False

    try:
        file_id = logo_url.split("/file/d/")[1].split("/")[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        logo_response = requests.get(download_url, timeout=10, stream=True)
        logo_response.raise_for_status()
        if "image" in logo_response.headers.get("content-type", ""):
            logo_img = BytesIO(logo_response.content)
            pdf.image(logo_img, x=150, y=10, w=50)
            logo_added = True
    except:
        pass

    if not logo_added and uploaded_logo:
        try:
            img_bytes = BytesIO(uploaded_logo.read())
            pdf.image(img_bytes, x=150, y=10, w=50)
        except:
            pass

    pdf.set_y(40)
    pdf.set_fill_color(255, 165, 0)
    pdf.cell(0, 10, txt="Payslip", ln=True, align='C', border=1, fill=True)
    pdf.set_fill_color(0, 174, 239)
    pdf.cell(0, 10, txt=data["company_name"], ln=True, align='C', border=1, fill=True)
    pdf.set_fill_color(135, 206, 250)
    pdf.cell(0, 10, txt=data["company_address"], ln=True, align='C', border=1, fill=True)
    pdf.ln(10)

    pdf.cell(95, 10, txt=f"Pay Date: {data['pay_date']}", ln=False, border=1)
    pdf.cell(95, 10, txt=f"Employee Name: {data['employee_name']}", ln=True, border=1)
    pdf.cell(95, 10, txt=f"Working Days: {data['working_days']}", ln=False, border=1)
    pdf.cell(95, 10, txt=f"Employee ID: {data['employee_id']}", ln=True, border=1)
    pdf.ln(10)

    pdf.set_fill_color(135, 206, 250)
    pdf.cell(95, 10, txt="Earnings", ln=False, border=1, fill=True)
    pdf.cell(90, 10, txt="Deductions", ln=True, border=1, fill=True)

    pdf.set_fill_color(240, 248, 255)
    pdf.cell(95, 10, txt=f"Basic Pay: {format_currency(data['basic_pay'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Tax: {format_currency(data['tax'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Housing: {format_currency(data['Housing'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Pension (Employee): {format_currency(data['employee_pension'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Transport: {format_currency(data['Transport'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Other Deductions: {format_currency(data['other_deductions'])}", ln=True, border=1)

    pdf.cell(95, 10, txt=f"Other Allowances: {format_currency(data['other_allowances'])}", ln=False, border=1)
    pdf.ln(10)

    total_earnings = data['basic_pay'] + data['Housing'] + data['Transport'] + data['other_allowances']
    total_deductions = data['tax'] + data['employee_pension'] + data['other_deductions']
    net_pay = total_earnings - total_deductions

    pdf.set_fill_color(144, 238, 144)
    pdf.cell(95, 10, txt=f"Total Earnings: {format_currency(total_earnings)}", ln=False, border=1, fill=True)
    pdf.set_fill_color(255, 182, 193)
    pdf.cell(90, 10, txt=f"Total Deductions: {format_currency(total_deductions)}", ln=True, border=1, fill=True)

    pdf.set_fill_color(173, 216, 230)
    pdf.cell(95, 10, txt=f"Net Pay: {format_currency(net_pay)}", ln=False, border=1, fill=True)

    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "This payslip is computer generated and does not require a physical signature.", 0, 0, 'C')

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    return pdf_bytes

# --- EMAIL UTILS ---
def send_email(recipient, subject, body, attachment_bytes, filename):
    msg = EmailMessage()
    msg['From'] = SENDER_EMAIL
    msg['To'] = recipient
    msg['Subject'] = subject
    msg.set_content(body)

    msg.add_attachment(attachment_bytes, maintype='application', subtype='pdf', filename=filename)

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

# --- STREAMLIT APP ---
def main():
    st.title("📤 Bulk Payslip Generator & Mailer")

    uploaded_logo = st.sidebar.file_uploader("Upload Company Logo (optional fallback)", type=["png", "jpg", "jpeg"])
    st.sidebar.info("Logo from Google Drive will be used by default. This is fallback only.")

    st.header("📁 Upload CSV with Employee Details")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    company_name = st.text_input("Company Name", value="Salmnine Investment Ltd")
    company_address = st.text_input("Company Address", value="FF Millennium Towers, VI, Lagos")
    pay_date = st.date_input("Pay Date", datetime.date.today())
    working_days = st.number_input("Working Days", value=30)

    if uploaded_file:
        df = pd.read_csv(uploaded_file)
        st.write("### 📊 Preview of Uploaded Data", df.head())

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📥 Generate Payslips Only"):
                for idx, row in df.iterrows():
                    data = {
                        "company_name": company_name,
                        "company_address": company_address,
                        "pay_date": pay_date.strftime("%Y-%m-%d"),
                        "working_days": working_days,
                        "employee_name": row['employee_name'],
                        "employee_id": row['employee_id'],
                        "basic_pay": row['basic_pay'],
                        "Housing": row['Housing'],
                        "Transport": row['Transport'],
                        "other_allowances": row['other_allowances'],
                        "tax": row['tax'],
                        "employee_pension": row['employee_pension'],
                        "other_deductions": row['other_deductions']
                    }
                    pdf_bytes = generate_pdf(data, uploaded_logo)
                    filename = f"{row['employee_name'].replace(' ', '_')}_payslip.pdf"
                    b64 = base64.b64encode(pdf_bytes).decode()
                    href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download {filename}</a>'
                    st.markdown(href, unsafe_allow_html=True)

        with col2:
            if st.button("📧 Email Payslips"):
                with st.spinner("Generating and sending emails..."):
                    for idx, row in df.iterrows():
                        data = {
                            "company_name": company_name,
                            "company_address": company_address,
                            "pay_date": pay_date.strftime("%Y-%m-%d"),
                            "working_days": working_days,
                            "employee_name": row['employee_name'],
                            "employee_id": row['employee_id'],
                            "basic_pay": row['basic_pay'],
                            "Housing": row['Housing'],
                            "Transport": row['Transport'],
                            "other_allowances": row['other_allowances'],
                            "tax": row['tax'],
                            "employee_pension": row['employee_pension'],
                            "other_deductions": row['other_deductions']
                        }

                        pdf_bytes = generate_pdf(data, uploaded_logo)
                        filename = f"{row['employee_name'].replace(' ', '_')}_payslip.pdf"
                        send_email(row['email'], "Your Monthly Payslip", "Please find attached your payslip.", pdf_bytes, filename)
                    st.success("Payslips emailed successfully!")

if __name__ == '__main__':
    main()
