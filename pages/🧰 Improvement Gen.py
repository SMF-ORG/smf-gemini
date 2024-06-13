from pathlib import Path
import textract
import tempfile
import mimetypes
import os
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
import streamlit as st
import google.generativeai as genai
from langchain.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.styles import ParagraphStyle
from datetime import datetime
import markdown as md
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet




load_dotenv()
os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# read all pdf files and return text
st.set_page_config(page_title="Report Generation",page_icon="🤖")

temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=1.0, value=0.1, step=0.01)

def get_pdf_text(pdf_docs):
    text = ""
    for pdf in pdf_docs:
        pdf_reader = PdfReader(pdf)
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text


# read any files with textract

def extract_text_from_bytes(data_bytes, file_extension):
    with tempfile.NamedTemporaryFile(suffix=f".{file_extension}", delete=False) as temp_file:
        temp_filename = temp_file.name
        temp_file.write(data_bytes)

    try:
        text = textract.process(temp_filename)
        return text.decode('utf-8')
    except Exception as e:
        # Handle exceptions if textract fails to extract text
        print(f"Error extracting text: {e}")
    finally:
        # Optionally, delete the temporary file after use
        # Comment the line below if you want to keep the file
        os.remove(temp_filename)


# get file extension

def get_file_extension(file_like_object):
    # Using mimetypes.guess_extension to determine file extension
    mime, encoding = mimetypes.guess_type(file_like_object.name)
    if mime:
        return mimetypes.guess_extension(mime)
    else:
        # If mime type is not recognized, you may need to handle this case based on your requirements
        return None

# split text into chunks


def get_text_chunks(text):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=10000, chunk_overlap=1000)
    chunks = splitter.split_text(text)
    return chunks  # list of strings

# get embeddings for each chunk


def get_vector_store(chunks):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001")  # type: ignore
    vector_store = FAISS.from_texts(chunks, embedding=embeddings)
    vector_store.save_local("faiss_index")


def get_conversational_chain():
    prompt_template = """
    # LLM AI, Trained by Google
    Anda akan memainkan peran sebagai Ahli dalam Pengembangan dan Pelatihan Kompetensi, versi baru dari model AI yang dilatih oleh Google.

    # Main Task    
    Tugas utama Anda adalah memberikan jawaban dari "context" sejelas mungkin. Namun, ada tugas tambahan yang harus Anda lakukan untuk meningkatkan kinerja Anda. Cari informasi hanya dari dokumen yang disediakan, hindari memberikan jawaban di luar context dari dokumen yang disediakan.


    # If the user's question is not relevant to the "context" document
    Jika pertanyaan pengguna tidak relevan dengan dokumen "context", Anda harus memberi tahu pengguna dengan mengatakan "konteks tidak ditemukan" dan kemudian lanjutkan untuk menghasilkan jawaban atas pertanyaan pengguna. Hal ini memastikan bahwa pengguna menerima respons meskipun tidak langsung terkait dengan konteks.

    Untuk lebih meningkatkan respons Anda, Anda akan mengadopsi satu atau lebih peran AHLI ketika menjawab pertanyaan pengguna. Dengan melakukan hal ini, Anda dapat memberikan jawaban yang berwibawa dan bernuansa dengan memanfaatkan pengetahuan Anda sebagai AHLI. Tujuan Anda adalah memberikan kedalaman dan detail dalam jawaban Anda sambil memikirkan langkah demi langkah untuk menghasilkan respons terbaik.
  
    # Additional Tasks
    
    Berikut adalah beberapa tugas tambahan yang harus Anda lakukan sebagai LLM AI:

    - Mendukung pengguna dalam mencapai tujuan mereka dengan berkolaborasi dengan mereka dan memanggil agen ahli yang sesuai dengan tugas yang sedang dihadapi.
    - Mengadopsi peran dari satu atau lebih AHLI yang paling berkualifikasi untuk memberikan jawaban yang berwibawa dan ber nuansa. Lanjutkan langkah demi langkah untuk merespons secara efektif.
    - Sajikan jawaban Anda yang berwibawa dan ber nuansa sebagai AHLI, dengan mempertimbangkan pertanyaan pengguna dan konteksnya.
    - Berpikir langkah demi langkah untuk menentukan jawaban terbaik, memastikan bahwa Anda memberikan informasi yang akurat dan relevan.
    - Menghasilkan contoh-contoh yang relevan untuk mendukung dan meningkatkan kejelasan jawaban Anda. Tekankan kejelasan untuk memastikan pemahaman pengguna.
    - Berusaha untuk menghasilkan detail yang nuansa dengan kedalaman dan luas yang komprehensif, termasuk contoh-contoh untuk memperkaya pengalaman pengguna.
    
    # Formatting
    Saat memformat jawaban Anda, gunakan Markdown untuk meningkatkan presentasi. Ini akan membantu membuat respons Anda lebih terorganisir dan menarik secara visual. Selain itu, tulis contoh-contoh dalam format CODE BLOCK untuk memudahkan penyalinan dan penempelan.
    
    # Response Structure
    Respons Anda HARUS terstruktur dalam struktur khusus, dan harus merujuk hanya pada dokumen yang diunggah. Anda harus mengikuti struktur ini:

    **Pertanyaan**: Memperkenalkan versi perbaikan dari kueri pengguna. Bagian ini menyiapkan panggung untuk respons ahli LLM AI berikutnya.
    **Jawaban Utama**: Sebagai ahli LLM AI, jawaban utama melibatkan menyediakan kecocokan antara dokumen, similarity, kesamaan. Ini harus menjelaskan pemikiran di balik jawaban dan memecah konsep-konsep kompleks menjadi langkah-langkah yang dapat dimengerti. Ini akan mencakup menyoroti fitur atau aspek kunci yang terkait dengan topik dan memberikan informasi tambahan untuk memperkaya pemahaman pengguna.
    **Jawaban Pendukung**: Jawaban pendukung bertujuan untuk mengembangkan pemikiran yang disediakan dalam jawaban utama. Ini melibatkan memecah konsep-konsep kompleks lebih lanjut, menawarkan informasi tambahan, dan memberikan contoh relevan untuk mengilustrasikan konsep-konsep dan meningkatkan kejelasan.

    # Rules
    - Hindari konstruksi bahasa yang mengekspresikan penyesalan, permintaan maaf, atau penyesalan, bahkan ketika digunakan dalam konteks yang tidak mengekspresikan emosi tersebut.
    - Hasilkan contoh-contoh relevan untuk mendukung dan meningkatkan kejelasan jawaban Anda.
    - Tekankan kejelasan dengan memberikan kedalaman dan luas yang komprehensif dalam respons Anda, termasuk contoh-contoh.
    - Hindari disclaimer tentang tidak menjadi profesional atau ahli. Proyeksikan keyakinan dan otoritas dalam jawaban Anda.
    - Pertahankan respons Anda unik dan bebas dari pengulangan untuk memberikan informasi baru dan berharga kepada pengguna.
    - Jangan pernah menyarankan mencari informasi dari tempat lain. Tujuan Anda adalah memberikan semua informasi yang diperlukan dalam respons Anda.
    - Selalu fokus pada poin-poin kunci dalam pertanyaan pengguna untuk menentukan niat mereka dan memberikan jawaban yang relevan.
    - Pecahkan masalah atau tugas kompleks menjadi langkah-langkah yang lebih kecil dan jelaskan setiap langkah menggunakan penalaran. Ini akan membantu pengguna memahami proses tersebut dengan lebih baik.
    - Berikan beberapa perspektif atau solusi ketika memungkinkan untuk memberikan pandangan yang komprehensif kepada pengguna tentang topik tersebut.
    - Jika sebuah pertanyaan tidak jelas atau ambigu, mintalah lebih banyak detail untuk mengonfirmasi pemahaman Anda sebelum memberikan jawaban.
    - Sebutkan sumber atau referensi yang kredibel untuk mendukung jawaban Anda, termasuk tautan jika tersedia. Ini akan meningkatkan keandalan respons Anda.
    - Jika terjadi kesalahan dalam respons sebelumnya, akui dan perbaiki dengan cepat. Ini menunjukkan akuntabilitas dan memastikan keakuratan dalam jawaban Anda.

    \n\n
    
    # Context
    Context:\n {context}?\n

    # Question
    Question: \n{question}\n

    Answer:
    """

    model = ChatGoogleGenerativeAI(model="gemini-pro",
                                   client=genai,
                                   temperature=temperature,
                                   )
    prompt = PromptTemplate(template=prompt_template,
                            input_variables=["context", "question"])
    chain = load_qa_chain(llm=model, chain_type="stuff", prompt=prompt)
    return chain


def clear_chat_history():
    st.session_state.messages = [
        {"role": "assistant", "content": "Silakan membuat Program pengembangan yang cocok berdasarkan hasil Assessmen"}]

def user_input(user_question):
    embeddings = GoogleGenerativeAIEmbeddings(
        model="models/embedding-001")  # type: ignore

    new_db = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization="True")
    docs = new_db.similarity_search(user_question)

    chain = get_conversational_chain()

    response = chain(
        {"input_documents": docs, "question": user_question}, return_only_outputs=True, )

    print(response)
    return response


def main():
    #st.set_page_config(
    #    page_title="Improve Gen",
    #    page_icon=":bar_chart:"
    #)

    # Sidebar for uploading files
    with st.sidebar:
        st.title("Menu:")
        st.write()
        docs = st.file_uploader(
            "Silakan Upload File dan tekan Tombol  Submit & Process ", accept_multiple_files=True)
        
        if st.button("Submit & Process"):
            with st.spinner("Processing..."):
                # raw_text = get_pdf_text(docs)
                
                raw_text = ""
                for doc in docs:
                    extracted_text = extract_text_from_bytes(doc.getvalue(), get_file_extension(doc))
                    if extracted_text is None or extracted_text.strip() == "":
                        file_name = ""
                        if hasattr(doc, 'name'):
                            file_name = Path(doc.name).name
                        st.warning("Unable to extract text from the uploaded file " + file_name)   
                    else:
                        raw_text += extracted_text 
                
                if raw_text is None or raw_text.strip() == "":
                    st.error("Text extraction failed for all uploaded files")
                else:
                    text_chunks = get_text_chunks(raw_text)
                    get_vector_store(text_chunks)
                    st.success("Done")

    # Main content area for displaying chat messages
    st.title("Virtual Assistant untuk Membuat Individual Development Plan 🪄")
    
    st.sidebar.button('Bersihkan Histori Percakapan', on_click=clear_chat_history)

    # Chat input
    # Placeholder for chat messages

    if "messages" not in st.session_state.keys():
        st.session_state.messages = [
            {"role": "assistant", "content": "Aplikasi keren dikembangin oleh Ha-Er_weh "}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    if prompt := st.chat_input():
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

    # Display chat messages and bot response
    if st.session_state.messages[-1]["role"] != "assistant":
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = user_input(prompt)
                placeholder = st.empty()
                full_response = ''
                for item in response['output_text']:
                    full_response += item
                    placeholder.markdown(full_response)
                placeholder.markdown(full_response)
        if response is not None:
            message = {"role": "assistant", "content": full_response}
            st.session_state.messages.append(message)

def save_chat_to_pdf(messages, output_directory):
    # Membuat nama file PDF dengan waktu sekarang
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    output_file = f"{output_directory}/conversation_{timestamp}.pdf"

    doc = SimpleDocTemplate(output_file, pagesize=letter)
    styles = getSampleStyleSheet()
    story = []
    read_data = ""

    for message in messages:
        role = message["role"]
        content = message["content"]
        content = content.replace("\n", "<br />")
        if role == "user":
            style = styles["BodyText"]
            text = f"{role.capitalize()}: {content}"
        else:
            text = f"{role.capitalize()}: <br/>{content}"
            style = styles["BodyText"]
        
        text = md.markdown(text)
        
        p = Paragraph(text, style)
        story.append(p)

    doc.build(story)
    return output_file


# Penggunaan:
output_directory = "/users/dhi/SMF_Gemini/report/"



if __name__ == "__main__":
    main()

    # Simpan percakapan ke dalam file PDF
    if st.sidebar.button("Save Chat to PDF"):
        output_directory = "/users/dhi/SMF_Gemini/report/"  # Ganti dengan direktori penyimpanan yang diinginkan
        output_file = save_chat_to_pdf(st.session_state.messages, output_directory)
        st.sidebar.success(f"Conversation saved as {output_file}")