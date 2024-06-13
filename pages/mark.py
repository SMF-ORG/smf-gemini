import streamlit as st
import markdown
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

# Fungsi untuk mengonversi Markdown ke HTML
def markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)

# Fungsi untuk mengonversi HTML ke elemen ReportLab
def html_to_pdf_elements(html_content):
    from bs4 import BeautifulSoup
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = []
    styles = getSampleStyleSheet()
    
    for tag in soup.find_all(['h1', 'p', 'li']):
        if tag.name == 'h1':
            elements.append(Paragraph(tag.text, styles['Title']))
        elif tag.name == 'p':
            elements.append(Paragraph(tag.text, styles['BodyText']))
        elif tag.name == 'li':
            elements.append(Paragraph(f"• {tag.text}", styles['BodyText']))
        elements.append(Spacer(1, 12))
    
    return elements

# Fungsi untuk menyimpan HTML sebagai file PDF menggunakan ReportLab
def save_as_pdf(html_content, output_path):
    elements = html_to_pdf_elements(html_content)
    doc = SimpleDocTemplate(output_path, pagesize=letter)
    doc.build(elements)

# Mendefinisikan tampilan Streamlit
def main():
    st.title("Aplikasi Streamlit untuk PDF")

    # Konten Markdown di aplikasi Streamlit
    markdown_text = """
    # Judul Utama

    Ini adalah paragraf dengan **teks tebal** dan *teks miring*.

    1. Ini adalah daftar nomor.
    2. Item kedua.

    """

    st.markdown(markdown_text)

    # Simpan konten Markdown sebagai file PDF
    if st.button("Simpan sebagai PDF"):
        html_content = markdown_to_html(markdown_text)
        save_as_pdf(html_content, "output.pdf")
        st.success("PDF berhasil disimpan!")

if __name__ == "__main__":
    main()
