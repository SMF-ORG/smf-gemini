import streamlit as st
import PyPDF2
import os

# Function to extract text from PDF
def read_pdf(file):
    with open(file, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        num_pages = len(pdf_reader.pages)
        content = ""
        for page_num in range(num_pages):
            content += pdf_reader.pages[page_num].extract_text()
        return content

# Function for file selection
def file_selector(folder_path='/users/dhi/SMF_Gemini/report/'):
    filenames = os.listdir(folder_path)
    selected_filename = st.selectbox('Select a file', filenames)
    if selected_filename:
        return os.path.join(folder_path, selected_filename)
    return None

# Streamlit app
def main():
    st.title("Menampilkan Laporan Final")

    # Option to upload a PDF file
    uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

    selected_file_path = None

    if uploaded_file is not None:
        # If file uploaded, use the uploaded file
        st.write('You uploaded `%s`' % uploaded_file.name)
        # Save the uploaded file to the specified folder
        with open(os.path.join('/users/dhi/SMF_Gemini/report/', uploaded_file.name), 'wb') as f:
            f.write(uploaded_file.getbuffer())
        selected_file_path = os.path.join('/users/dhi/SMF_Gemini/report/', uploaded_file.name)
    else:
        # If no file uploaded, provide option to select from folder
        selected_file_path = file_selector()
        if selected_file_path:
            st.write('You selected `%s`' % os.path.basename(selected_file_path))

    # Read PDF and extract text if a file is selected
    if selected_file_path:
        try:
            content = read_pdf(selected_file_path)
            st.subheader("Extracted Text:")
            st.text(content)
        except Exception as e:
            st.error(f"An error occurred while reading the PDF: {e}")

if __name__ == "__main__":
    main()
