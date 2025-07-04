import streamlit as st
import openai
#from decouple import config
from fpdf import FPDF
from docx import Document
from PyPDF2 import PdfReader
import io
import chardet
import os
import time
from config import OPENAI_API_KEY

# Load the API key from the .env file
api_key = OPENAI_API_KEY

# Set up OpenAI API key
openai.api_key = api_key

# Function to detect and get the encoding of the text
def detect_text_encoding(text):
    result = chardet.detect(text)
    return result["encoding"]

# Function for document summarization
def document_summarization(document_text):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Summarize the following document to highlight the key points and main ideas making it easier to understand:\n{document_text}",
        max_tokens=150
    )
    return response.choices[0].text

# Function for entity recognition
def extract_entities(document_text):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Identify entities, names, locations in the following document:\n{document_text}"
    )
    return response.choices[0].text

# Function for question-answering
def answer_questions(document_text, user_question):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Answer the following question based on the document:\nDocument: {document_text}\nQuestion: {user_question}"
    )
    return response.choices[0].text

# Function for sentiment analysis
def analyze_sentiment(document_text):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=f"Analyze the sentiment of the following document:\n{document_text}"
    )
    return response.choices[0].text

# Function to save summarized content to PDF
def save_to_pdf(content, filename):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(190, 10, txt=content, align="L")
    pdf.output(filename)

    # Get the path to the user's Downloads folder
    downloads_path = os.path.expanduser("~" + os.sep + "Downloads")

    # Save the PDF file in the Downloads folder
    pdf.output(os.path.join(downloads_path, filename))

# Function to save summarized content to Word document
def save_to_word(content, filename):
    doc = Document()
    doc.add_paragraph(content)
    doc.save(filename)

# Streamlit UI with background image
st.markdown(
    """
    <style>
    body {
        background-image: url("images/background.jpeg");
        background-size: cover;
    }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("Insightful Analytics")
st.subheader("Document Summarizer and Analysis")

# Provide an introduction to the app
st.markdown("Welcome to Insightful Analytics App. This app allows you to summarize, analyze sentiment, perform entity recognition, and answer your questions based on provided text/document data. You can either manually input your text or upload a document for analysis.")

# Choose between manual input and document upload
input_choice = st.radio("Choose an option:", ("Manually Input Text", "Upload a Document"))

# User manual input
if input_choice == "Manually Input Text":
    user_input = st.text_area("Manually input your text:")

    if st.button("Sentiment Analysis"):
        st.subheader("Sentiment Analysis:")
        sentiment = analyze_sentiment(user_input)
        st.write(sentiment)

    if st.button("Entity Recognition"):
        st.subheader("Entities:")
        entities = extract_entities(user_input)
        st.write(entities)

    user_question = st.text_input("Ask a question on information in the document document:")
    if st.button("Answer Question"):
        st.subheader("Answer:")
        answer = answer_questions(user_input, user_question)
        st.write(answer)

    if st.button("Summarize Text"):
        st.subheader("Summary:")
        # Detect the encoding of the document
        encoding = detect_text_encoding(user_input.encode("utf-8"))
        summary = document_summarization(user_input)
        st.write(summary)

        if st.button("Download Summary as PDF"):
            summary = document_summarization(user_input.decode("utf-8"))
            save_to_pdf(summary, f"summary.pdf")
            st.success("Summary Saved! Check Downloads Folder.")

        if st.button("Download Summary as Word"):
            summary = document_summarization(user_input.decode("utf-8"))
            save_to_word(summary, f"summary.docx")
            st.success("Summary Saved! Check Downloads Folder.")

if input_choice == "Upload a Document":
    uploaded_file = st.file_uploader("Upload a legal document (TXT, PDF, or DOCX)", type=["txt", "pdf", "docx"])

    if uploaded_file is not None:
        file_content = uploaded_file.read()

        success_message = st.success("File successfully uploaded.")
        time.sleep(1)
        success_message.empty()
        
        if uploaded_file.type == "text/plain" or uploaded_file.type == "application/pdf" or uploaded_file.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            st.subheader("Uploaded Document:")

            if file_content:
                # Display the first few words of the document when 'Review' button is clicked
                if st.button("Review Document"):
                    if uploaded_file.type == "application/pdf":
                        reader = PdfReader(io.BytesIO(file_content))
                        st.write(reader.pages[0].extract_text()[:1000])
                    else:
                        # Detect and use the correct encoding
                        encoding = detect_text_encoding(file_content)
                        st.write(file_content.decode(encoding)[:1000])

                if st.button("Sentiment Analysis"):
                    st.subheader("Sentiment Analysis:")
                    sentiment = analyze_sentiment(file_content.decode("utf-8"))
                    st.write(sentiment)

                if st.button("Entity Recognition"):
                    st.subheader("Entities:")
                    entities = extract_entities(file_content.decode("utf-8"))
                    st.write(entities)

                user_question = st.text_input("Ask a question on information in the document document:")
                if st.button("Answer Question"):
                    st.subheader("Answer:")
                    answer = answer_questions(file_content.decode("utf-8"), user_question)
                    st.write(answer)

                if st.button("Summarize Document"):
                    st.subheader("Summary:")
                    # Detect the encoding of the document
                    encoding = detect_text_encoding(file_content)
                    summary = document_summarization(file_content)
                    st.write(summary)

                    if st.button("Download Summary as PDF"):
                        summary = document_summarization(file_content.decode("utf-8"))
                        save_to_pdf(summary, f"Summary {uploaded_file.name}.pdf")
                        st.success("Summary Saved! Check Downloads Folder.")

                    if st.button("Download Summary as Word"):
                        summary = document_summarization(file_content.decode("utf-8"))
                        save_to_word(summary, f"Summary {uploaded_file.name}.docx")
                        st.success("Summary Saved!")
            else:
                st.warning("The uploaded file is empty.")
        else:
            st.warning("Invalid file format. Please upload a TXT, PDF, or DOCX file.")
