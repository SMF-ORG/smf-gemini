import streamlit as st
import markdown
from weasyprint import HTML


# Fungsi untuk mengonversi Markdown ke HTML
def markdown_to_html(markdown_text):
    return markdown.markdown(markdown_text)

# Fungsi untuk menyimpan HTML sebagai file PDF
def save_as_pdf(html_content, output_path):
    HTML(string=html_content).write_pdf(output_path)

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