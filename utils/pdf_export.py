import os
from datetime import datetime
import markdown
from fpdf import FPDF
import unicodedata

class PDF(FPDF):
    def header(self):
        self.set_font("helvetica", "B", 12)
        self.cell(0, 10, "Autonomous Research Report", border=False, ln=1, align="C")
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

def sanitize_text(text: str) -> str:
    # fpdf2 core fonts only support latin-1 equivalent. Normalizing standard unicode:
    text = text.replace('“', '"').replace('”', '"').replace('‘', "'").replace('’', "'")
    text = text.replace('—', '-').replace('–', '-')
    text = text.replace('•', '-') # common bullet point replacement
    # Encode ignoring anything else to prevent crash
    return text.encode('latin-1', 'replace').decode('latin-1')

def generate_pdf(topic: str, markdown_content: str, search_results: list, output_filename: str = "report.pdf") -> str:
    pdf = PDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("helvetica", "B", 16)
    safe_topic = sanitize_text(topic)
    pdf.multi_cell(0, 10, safe_topic, align="C")
    
    # Date
    pdf.set_font("helvetica", "I", 10)
    current_date = datetime.now().strftime("%B %d, %Y")
    pdf.cell(0, 10, f"Generated on: {current_date}", ln=1, align="C")
    pdf.ln(5)
    
    safe_md = sanitize_text(markdown_content)
    html_content = markdown.markdown(safe_md)
    
    pdf.set_font("helvetica", size=11)
    
    # Use a fresh PDF to safely test HTML rendering without corrupting main PDF state
    test_pdf = PDF()
    test_pdf.add_page()
    test_pdf.set_font("helvetica", size=11)
    
    html_success = False
    try:
        test_pdf.write_html(html_content)
        html_success = True
    except Exception as e:
        print(f"HTML rendering error: {e}")
        
    if html_success:
        pdf.write_html(html_content)
    else:
        pdf.multi_cell(0, 6, text=safe_md)
        
    pdf.ln(10)
    
    # Citations
    pdf.set_font("helvetica", "B", 14)
    pdf.cell(0, 10, "References", ln=1)
    
    pdf.set_font("helvetica", size=10)
    for i, res in enumerate(search_results, 1):
        url = res.get("url", "No URL provided")
        url = sanitize_text(url)
        # Truncate visual text to prevent running off page, but keep the full link active
        display_url = url if len(url) <= 85 else url[:82] + "..."
        pdf.cell(0, 6, f"[{i}] {display_url}", ln=1, link=str(url))
        
    pdf.output(output_filename)
    return output_filename
