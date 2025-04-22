import streamlit as st
import pandas as pd
import datetime
from fpdf import FPDF
import base64
from io import BytesIO
import requests
import smtplib
from email.message import EmailMessage
import tempfile

SENDER_EMAIL = "petmartian@gmail.com"
SENDER_PASSWORD = "salarypayslip1"
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# --- UTILS ---
def format_currency(amount):
    return f"{amount:,.2f}"

def safe_float(val):
    try:
        return float(val)
    except:
        return 0.0

def load_data(uploaded_file):
    if uploaded_file.name.endswith('.csv'):
        return pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        return pd.read_excel(uploaded_file)
    else:
        st.error("Unsupported file format. Please upload a CSV or Excel file.")
        return None

# --- PDF GENERATOR ---
def generate_pdf(data):
    pdf = FPDF()
    pdf.add_page()

    # Add background letterhead image
    letterhead_url = "https://drive.google.com/file/d/1vTojAg8yf9J8SGEncECfgi1HXquuokzH/view?usp=sharing"
    try:
        file_id = letterhead_url.split("/file/d/")[1].split("/")[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        bg_response = requests.get(download_url, timeout=10, stream=True)
        bg_response.raise_for_status()
        if "image" in bg_response.headers.get("content-type", ""):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_bg:
                tmp_bg.write(bg_response.content)
                tmp_bg.flush()
                pdf.image(tmp_bg.name, x=0, y=0, w=210, h=297)
    except Exception as e:
        print("Background image failed:", e)

    # Add Logo
    logo_url = "https://drive.google.com/file/d/1melsj54pPwsjmYGRE1SQg7EBLZ6BthCn/view?usp=drive_link"
    try:
        file_id = logo_url.split("/file/d/")[1].split("/")[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        logo_response = requests.get(download_url, timeout=10, stream=True)
        logo_response.raise_for_status()
        if "image" in logo_response.headers.get("content-type", ""):
            with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_logo:
                tmp_logo.write(logo_response.content)
                tmp_logo.flush()
                pdf.image(tmp_logo.name, x=150, y=10, w=40)
    except Exception as e:
        print("Logo download failed:", e)

    pdf.ln(30)

    pdf.set_font("Arial", style="B", size=18)
    pdf.cell(0, 15, txt="PAYSLIP", ln=True, align='C', border=1)
    pdf.ln(5)

    pdf.set_font("Arial", style="", size=12)
    pdf.cell(0, 10, txt=data["company_name"], ln=True, align='C', border=1)
    pdf.cell(0, 10, txt=data["company_address"], ln=True, align='C', border=1)
    pdf.ln(10)

    pdf.cell(95, 10, txt=f"Pay Date: {data['pay_date']}", ln=False, border=1)
    pdf.cell(95, 10, txt=f"Employee Name: {data['employee_name']}", ln=True, border=1)
    pdf.cell(95, 10, txt=f"Working Days: {data['working_days']}", ln=False, border=1)
    pdf.cell(95, 10, txt=f"Employee ID: {data['employee_id']}", ln=True, border=1)
    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(95, 10, txt="EARNINGS", ln=False, border=1)
    pdf.cell(90, 10, txt="DEDUCTIONS", ln=True, border=1)

    pdf.set_font("Arial", size=12)

    pdf.cell(95, 10, txt=f"Basic Pay: {format_currency(data['basic_pay'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Tax: {format_currency(data['tax'])}", ln=True, border=1)
    pdf.cell(95, 10, txt=f"Housing: {format_currency(data['Housing'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Pension (Employee): {format_currency(data['employee_pension'])}", ln=True, border=1)
    pdf.cell(95, 10, txt=f"Transport: {format_currency(data['Transport'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Other Deductions: {format_currency(data['other_deductions'])}", ln=True, border=1)
    pdf.cell(95, 10, txt=f"Other Allowances: {format_currency(data['other_allowances'])}", ln=False, border=1)
    pdf.ln(10)

    pdf.set_font("Arial", style="B", size=12)
    pdf.cell(95, 10, txt=f"Total Earnings: {format_currency(data['total_earnings'])}", ln=False, border=1)
    pdf.cell(90, 10, txt=f"Total Deductions: {format_currency(data['total_deductions'])}", ln=True, border=1)

    pdf.ln(5)
    pdf.set_font("Arial", style="B", size=14)
    pdf.cell(0, 12, txt=f"Net Pay: {format_currency(data['net_pay'])}", ln=True, border=1, align='C')

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
    st.set_page_config(page_title="Payslip Generator & Mailer", page_icon="📤", layout="wide")

    hide_streamlit_style = """
        <style>
        [data-testid="stSidebar"] {display: none;}
        [data-testid="collapsedControl"] {display: none;}
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
            padding-left: 5rem;
            padding-right: 5rem;
        }
        </style>
        """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; font-size: 3rem;'>📤 Bulk Payslip Generator & Mailer</h1>", unsafe_allow_html=True)
    st.markdown("---")

    st.markdown("### 📁 Upload Employee Details (CSV or Excel)")

    uploaded_file = st.file_uploader("Upload File", type=["csv", "xlsx"], label_visibility="collapsed")

    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            company_name = st.text_input("🏢 Company Name", value="Salmnine Investment Ltd")
            company_address = st.text_input("📍 Company Address", value="FF Millennium Towers, VI, Lagos")
        with col2:
            pay_date = st.date_input("📅 Pay Date", datetime.date.today())
            working_days = st.number_input("📆 Working Days", value=30, min_value=1, max_value=31)

    if uploaded_file:
        df = load_data(uploaded_file)
        if df is not None:
            st.success(f"✅ {len(df)} employees loaded successfully!")
            st.markdown("### 👀 Preview of Uploaded Data")
            st.dataframe(df, use_container_width=True)

            generate_col, email_col = st.columns(2)

            with generate_col:
                if st.button("📥 Generate Payslips", use_container_width=True):
                    for idx, row in df.iterrows():
                        data = {
                            "company_name": company_name,
                            "company_address": company_address,
                            "pay_date": pay_date.strftime("%Y-%m-%d"),
                            "working_days": working_days,
                            "employee_name": row['employee_name'],
                            "employee_id": row['employee_id'],
                            "basic_pay": safe_float(row['basic_pay']),
                            "Housing": safe_float(row['Housing']),
                            "Transport": safe_float(row['Transport']),
                            "other_allowances": safe_float(row['other_allowances']),
                            "tax": safe_float(row['tax']),
                            "employee_pension": safe_float(row['employee_pension']),
                            "other_deductions": safe_float(row['other_deductions']),
                            "total_earnings": safe_float(row['total_earnings']),
                            "total_deductions": safe_float(row['total_deductions']),
                            "net_pay": safe_float(row['net_pay'])
                        }
                        pdf_bytes = generate_pdf(data)
                        filename = f"{row['employee_name'].replace(' ', '_')}_payslip.pdf"
                        b64 = base64.b64encode(pdf_bytes).decode()
                        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download {filename}</a>'
                        st.markdown(href, unsafe_allow_html=True)

            with email_col:
                if st.button("📧 Email Payslips", use_container_width=True):
                    with st.spinner("⏳ Sending Payslips..."):
                        progress = st.progress(0)
                        for idx, row in df.iterrows():
                            data = {
                                "company_name": company_name,
                                "company_address": company_address,
                                "pay_date": pay_date.strftime("%Y-%m-%d"),
                                "working_days": working_days,
                                "employee_name": row['employee_name'],
                                "employee_id": row['employee_id'],
                                "basic_pay": safe_float(row['basic_pay']),
                                "Housing": safe_float(row['Housing']),
                                "Transport": safe_float(row['Transport']),
                                "other_allowances": safe_float(row['other_allowances']),
                                "tax": safe_float(row['tax']),
                                "employee_pension": safe_float(row['employee_pension']),
                                "other_deductions": safe_float(row['other_deductions']),
                                "total_earnings": safe_float(row['total_earnings']),
                                "total_deductions": safe_float(row['total_deductions']),
                                "net_pay": safe_float(row['net_pay'])
                            }
                            pdf_bytes = generate_pdf(data)
                            filename = f"{row['employee_name'].replace(' ', '_')}_payslip.pdf"
                            send_email(row['email'], "Your Monthly Payslip", "Please find attached your payslip.", pdf_bytes, filename)
                            progress.progress((idx + 1) / len(df))
                        st.success("🎉 All Payslips Sent Successfully!")

if __name__ == '__main__':
    main()
