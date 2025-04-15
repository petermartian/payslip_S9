import streamlit as st
import datetime
from fpdf import FPDF
import base64
from io import BytesIO
import requests


# ======= Utility Functions =======

def format_currency(amount):
    """Formats the amount with commas, without Naira sign."""
    return f"{amount:,.2f}"


def generate_pdf(data, uploaded_logo=None):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # === Try Google Drive Logo First ===
    logo_url = "https://drive.google.com/file/d/1melsj54pPwsjmYGRE1SQg7EBLZ6BthCn/view?usp=drive_link"
    logo_added = False

    try:
        file_id = logo_url.split("/file/d/")[1].split("/")[0]
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
        logo_response = requests.get(download_url, timeout=10, stream=True)
        logo_response.raise_for_status()

        content_type = logo_response.headers.get("content-type", "")
        if "image" in content_type:
            logo_img = BytesIO(logo_response.content)
            pdf.image(logo_img, x=150, y=10, w=50)
            logo_added = True
    except:
        pass

    # === Fallback to uploaded logo ===
    if not logo_added and uploaded_logo is not None:
        try:
            img_bytes = BytesIO(uploaded_logo.read())
            pdf.image(img_bytes, x=150, y=10, w=50)
            logo_added = True
        except Exception as e:
            st.warning(f"Failed to load uploaded logo: {e}")

    # === Header ===
    pdf.set_y(40)
    pdf.set_fill_color(255, 165, 0)
    pdf.cell(0, 10, txt="Payslip", ln=True, align='C', border=1, fill=True)

    pdf.set_fill_color(0, 174, 239)
    pdf.cell(0, 10, txt=data["company_name"], ln=True, align='C', border=1, fill=True)

    pdf.set_fill_color(135, 206, 250)
    pdf.cell(0, 10, txt=data["company_address"], ln=True, align='C', border=1, fill=True)
    pdf.ln(10)

    # === Employee Details ===
    pdf.set_fill_color(240, 248, 255)
    pdf.cell(95, 10, txt=f"Pay Date: {data['pay_date']}", ln=False, border=1)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(95, 10, txt=f"Employee Name: {data['employee_name']}", ln=True, border=1)
    pdf.set_font("Arial", size=12)
    pdf.cell(95, 10, txt=f"Working Days: {data['working_days']}", ln=False, border=1)
    pdf.set_font("Arial", 'B', size=12)
    pdf.cell(95, 10, txt=f"Employee ID: {data['employee_id']}", ln=True, border=1)
    pdf.set_font("Arial", size=12)
    pdf.ln(10)

    # === Earnings & Deductions ===
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

    pdf.set_fill_color(144, 238, 144)
    pdf.cell(95, 10, txt=f"Total Earnings: {format_currency(data['total_earnings'])}", ln=False, border=1, fill=True)
    pdf.set_fill_color(255, 182, 193)
    pdf.cell(90, 10, txt=f"Total Deductions: {format_currency(data['total_deductions'])}", ln=True, border=1, fill=True)

    pdf.set_fill_color(173, 216, 230)
    pdf.cell(95, 10, txt=f"Net Pay: {format_currency(data['net_pay'])}", ln=False, border=1, fill=True)

    # === Footer/Signature ===
    pdf.set_y(-30)
    pdf.set_font("Arial", 'I', 10)
    pdf.cell(0, 10, "This payslip is computer generated and does not require a physical signature.", 0, 0, 'C')

    pdf_bytes = pdf.output(dest='S').encode('latin1')
    pdf_base64 = base64.b64encode(pdf_bytes).decode('utf-8')
    return pdf_base64


# ======= Streamlit UI =======

def main():
    st.title("💼 S9 Payslip Generator")

    # Logo uploader
    st.sidebar.image("https://cdn-icons-png.flaticon.com/512/4322/4322991.png", width=100)
    st.sidebar.header("🔧 Logo Configuration")
    uploaded_logo = st.sidebar.file_uploader("Upload Logo (fallback)", type=["png", "jpg", "jpeg"])

    # Header
    st.header("📌 Header Details")
    company_name = st.text_input("Company Name", value="Salmnine Investment Ltd")
    company_address = st.text_input("Company Address", value="FF Millennium Towers, Ligali Ayorinde, VI, Lagos")

    # Employee Info
    st.header("👤 Employee Details")
    col1, col2 = st.columns(2)
    with col1:
        employee_name = st.text_input("Employee Name", value="James Arthur")
        employee_id = st.text_input("Employee ID", value="0077")
    with col2:
        pay_date = st.date_input("Pay Date", datetime.date.today())
        working_days = st.number_input("Working Days", value=30)

    # Salary Info
    st.header("💰 Salary Breakdown")
    col3, col4 = st.columns(2)
    with col3:
        basic_pay = st.number_input("Basic Pay", value=400000)
        Housing = st.number_input("Housing", value=200000)
        Transport = st.number_input("Transport", value=150000)
        other_allowances = st.number_input("Other Allowances", value=25000)
    with col4:
        tax = st.number_input("Tax", value=100000)
        employee_pension = st.number_input("Pension (Employee)", value=57000)
        other_deductions = st.number_input("Other Deductions", value=0)

    # Calculations
    total_earnings = basic_pay + Housing + Transport + other_allowances
    total_deductions = tax + employee_pension + other_deductions
    net_pay = total_earnings - total_deductions

    st.subheader("📈 Net Pay")
    st.success(f"₦ {format_currency(net_pay)}")

    # PDF Generation
    if st.button("🧾 Generate Payslip PDF"):
        data = {
            "company_name": company_name,
            "company_address": company_address,
            "pay_date": pay_date.strftime("%Y-%m-%d"),
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

        pdf_base64 = generate_pdf(data, uploaded_logo)
        st.markdown(
            f'<a href="data:application/pdf;base64,{pdf_base64}" download="payslip.pdf">📥 Download Payslip PDF</a>',
            unsafe_allow_html=True
        )


if __name__ == "__main__":
    main()
