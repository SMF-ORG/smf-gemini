import streamlit as st
import fitz
from io import BytesIO

st.set_page_config(
    page_title="Hello",
    page_icon="👋",
)

st.write("# Selamat Datang di Aplikasi Keren Kecerdasan Buatan untuk Assessment Pengembangan! 👋")
judul="**Bagian Ini untuk menggabungkan hasil laporan terpadu:"

st.markdown(
    """ Silakan Gabungkan 2 laporan dari hasil Building report dan Improvement""")




def merge_pdfs(pdf_a, pdf_b, pdf_c, output_filename):
    with open(output_filename, "wb") as output_file:
        doc_a = fitz.open(stream=pdf_a.read(), filetype="pdf")
        doc_b = fitz.open(stream=pdf_b.read(), filetype="pdf")
        doc_c = fitz.open(stream=pdf_c.read(), filetype="pdf")
        doc_a.insert_pdf(doc_b)
        doc_a.insert_pdf(doc_c)
        doc_a.save(output_file)
        
def main():
    st.title("PDF Merger App")
    
    st.sidebar.header("Merge PDFs")
    pdf_a = st.sidebar.file_uploader("Upload 1st PDF", type="pdf")
    pdf_b = st.sidebar.file_uploader("Upload 2nd PDF", type="pdf")
    pdf_c = st.sidebar.file_uploader("Upload 3rd PDF", type="pdf")
    output_dir = "/users/dhi/SMF_GEMINI/report/"  # Direktori tempat Anda ingin menyimpan file
    output_filename = st.sidebar.text_input("Output Filename", "/users/dhi/SMF_GEMINI/report/merged.pdf")

    if st.sidebar.button("Merge"):
        if pdf_a and pdf_b:
            merge_pdfs(pdf_a, pdf_b, pdf_c, output_filename)
            st.sidebar.success("PDFs merged successfully!")
        else:
            st.sidebar.error("Please upload both PDFs.")

if __name__ == "__main__":
    main()