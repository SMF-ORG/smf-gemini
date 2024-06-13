import streamlit as st
import fitz
import os
from io import BytesIO

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Selamat Datang di Aplikasi Keren Kecerdasan Buatan untuk Assessment Pengembangan! 👋")
judul = "**Bagian Ini untuk menggabungkan hasil laporan terpadu:"

st.markdown(
    """Silakan Gabungkan 2 laporan dari hasil Building report dan Improvement"""
)

def merge_pdfs(pdf_a, pdf_b, pdf_c, output_filename):
    doc_a = fitz.open(stream=pdf_a.read(), filetype="pdf")
    doc_b = fitz.open(stream=pdf_b.read(), filetype="pdf")
    doc_c = fitz.open(stream=pdf_c.read(), filetype="pdf")
    doc_a.insert_pdf(doc_b)
    doc_a.insert_pdf(doc_c)
    doc_a.save(output_filename)
    doc_a.close()
    doc_b.close()
    doc_c.close()

def main():
    st.title("PDF Merger App")

    st.sidebar.header("Merge PDFs")
    pdf_a = st.sidebar.file_uploader("Upload 1st PDF", type="pdf")
    pdf_b = st.sidebar.file_uploader("Upload 2nd PDF", type="pdf")
    pdf_c = st.sidebar.file_uploader("Upload 3rd PDF", type="pdf")

    output_directory = "./files"
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    file_name = st.sidebar.text_input("Nama file output PDF (tanpa .pdf)", "merged")
    output_filename = os.path.join(output_directory, f"{file_name}.pdf")

    if st.sidebar.button("Merge and Save"):
        if pdf_a and pdf_b and pdf_c:
            try:
                merge_pdfs(pdf_a, pdf_b, pdf_c, output_filename)
                st.sidebar.success(f"PDFs merged successfully and saved as {output_filename}")
                # st.sidebar.markdown(f"📥 [Unduh file PDF]({output_filename})")
            except Exception as e:
                st.sidebar.error(f"Error: {e}")
        else:
            st.sidebar.error("Please upload all three PDFs.")

if __name__ == "__main__":
    main()
