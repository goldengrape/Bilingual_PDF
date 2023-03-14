import streamlit as st
from main import process_book
import fitz
import os
import platform 
import subprocess
# import io import BytesIO

st.title("PDF Bilingual Translator")
col1,col2=st.columns(2)
file=col1.file_uploader("Upload a PDF file", type="pdf")
col21,col22=col2.columns([1,2])
start_page=col21.text_input("Start Page",1)
end_page=col21.text_input("End Page",1)
source_language=col22.selectbox("Target Language",["English","Chinese"])
target_language=col22.selectbox("Target Language",["Chinese","English"])

OPENAI_API_KEY=st.text_input("OpenAI API KEY",type="password")
translate_button=st.button("Translate")


start_page=int(start_page)-1
end_page=int(end_page)-1
htmltopdf= subprocess.run(['which', 'wkhtmltopdf'], stdout=subprocess.PIPE)
print(htmltopdf)
st.write(htmltopdf.stdout.decode('utf-8'))
# if platform.system() == "Windows":
#     htmltopdf=r"C:\\Program Files\\wkhtmltopdf\\bin\\wkhtmltopdf.exe"
# else:
#     # htmltopdf='/usr/local/bin/wkhtmltopdf'
#     htmltopdf='/home/appuser/venv/bin/wkhtmltopdf'

if file is not None:
    filename=file.name
    with open(filename, "wb") as f:
        f.write(file.getvalue())
    source_doc = fitz.open(filename)
    if end_page<0:
        end_page=source_doc.page_count-1
    output_filename=filename.replace(".pdf","_Bilingual.pdf")

if translate_button:
    with st.spinner("Translating..."):
        process_book(source_doc,start_page,end_page,output_filename,htmltopdf,source_language,target_language)
        with open(output_filename, "rb") as f:
            translated_pdf = f.read()
        st.download_button(label="Download", data=translated_pdf, file_name=output_filename, mime="application/pdf")
