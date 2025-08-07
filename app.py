from dotenv import load_dotenv
load_dotenv()

import base64
import streamlit as st
import os
import io
from PIL import Image
import fitz  # PyMuPDF
import google.generativeai as genai

# Configure Gemini API
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# Get Gemini response
def get_gemini_response(input_text, pdf_content, prompt):
    model = genai.GenerativeModel('gemini-pro-vision')
    response = model.generate_content([input_text, pdf_content[0], prompt])
    return response.text

# Convert uploaded PDF's first page to JPEG (base64)
def input_pdf_setup(uploaded_file):
    if uploaded_file is not None:
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        first_page = doc.load_page(0)
        pix = first_page.get_pixmap()
        img_byte_arr = io.BytesIO(pix.tobytes("jpeg"))
        img_byte_arr = img_byte_arr.getvalue()

        pdf_parts = [
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(img_byte_arr).decode()
            }
        ]
        return pdf_parts
    else:
        raise FileNotFoundError("No file uploaded")

# Streamlit App
st.set_page_config(page_title="ATS Resume Expert")
st.header("ATS Tracking System")

input_text = st.text_area("Job Description:", key="job_description_input")
uploaded_file = st.file_uploader("Upload your resume (PDF)...", type=["pdf"], key="resume_uploader")

if uploaded_file is not None:
    st.success("✅ PDF Uploaded Successfully")

submit1 = st.button("Tell Me About the Resume", key="btn_summary")
submit3 = st.button("Percentage Match", key="btn_match")

input_prompt1 = """
You are an experienced Technical Human Resource Manager. Your task is to review the provided resume against the job description. 
Please share your professional evaluation on whether the candidate's profile aligns with the role. 
Highlight the strengths and weaknesses of the applicant in relation to the specified job requirements.
"""

input_prompt3 = """
You are a skilled ATS (Applicant Tracking System) scanner with a deep understanding of data science and ATS functionality. 
Your task is to evaluate the resume against the provided job description. 
Give me the percentage of match, followed by missing keywords, and finally your concluding thoughts.
"""

# Handle summary request
if submit1:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt1)
        st.subheader("🔍 Resume Review")
        st.write(response)
    else:
        st.warning("⚠️ Please upload the resume.")

# Handle match percentage request
elif submit3:
    if uploaded_file is not None:
        pdf_content = input_pdf_setup(uploaded_file)
        response = get_gemini_response(input_text, pdf_content, input_prompt3)
        st.subheader("📊 Resume Matching Percentage")
        st.write(response)
    else:
        st.warning("⚠️ Please upload the resume.")
