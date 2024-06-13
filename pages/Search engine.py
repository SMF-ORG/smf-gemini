import streamlit as st
import PyPDF2
import os

# Function to extract text from PDF
def read_pdf(file):
    pdf_reader = PyPDF2.PdfReader(file)
    num_pages = len(pdf_reader.pages)
    content = ""
    for page_num in range(num_pages):
        content += pdf_reader.pages[page_num].extract_text()
    return content

# Function for file selection
def file_selector(folder_path='/users/dhi/SMF_Gemini/report/'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    return os.path.join(folder_path, selected_filename)

# Streamlit app
def main():
    st.title("Menampilkan Laporan Final")

    # Option to upload a PDF file
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    if uploaded_file is None:
        # If no file uploaded, provide option to select from folder
        selected_file_path = file_selector()
        selected_file_name = os.path.basename(selected_file_path)
        st.write('You selected `%s`' % selected_file_name)
    else:
        # If file uploaded, use the uploaded file
        selected_file_name = uploaded_file.name
        st.write('You uploaded `%s`' % selected_file_name)

    # Read PDF and extract text if a file is selected
    if selected_file_name:
        selected_file_path = os.path.join('/users/dhi/SMF_Gemini/report/', selected_file_name)
        content = read_pdf(selected_file_path)
        st.subheader("Extracted Text:")
        st.text(content)

if __name__ == "__main__":
    main()