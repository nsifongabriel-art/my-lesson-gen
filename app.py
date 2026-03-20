import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

# --- Function to create the Word Doc ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Generated Academic Material', 0)
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Edu-Planner Pro", layout="wide")
st.title("🍎 Edu-Planner: Scheme to Exam")

api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
mode = st.sidebar.selectbox("Select Output Type", 
    ["Weekly Notes of Lesson", "Weekly Test", "Midterm Project", "Final Examination"])

scheme_input = st.text_area("Paste Scheme of Work here...", height=150)
grade = st.text_input("Grade Level")

# Persistent storage for the result
if 'generated_content' not in st.session_state:
    st.session_state['generated_content'] = ""

if st.button("Generate"):
    if not api_key or not scheme_input:
        st.error("Missing API Key or Scheme!")
    else:
        client = Groq(api_key=api_key)
        
        # System instructions based on mode
        prompts = {
            "Weekly Notes of Lesson": "Create detailed weekly notes for this scheme with examples and classwork.",
            "Weekly Test": "Create a 10-question quiz with an answer key based on this scheme.",
            "Midterm Project": "Design a mid-term project and grading rubric for this scheme.",
            "Final Examination": "Create a full exam (Objectives and Theory) for this scheme."
        }

        with st.spinner("Processing..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are an expert educator."},
                    {"role": "user", "content": f"{prompts[mode]} Grade: {grade}. Scheme: {scheme_input}"}
                ]
            )
            st.session_state['generated_content'] = completion.choices[0].message.content

# --- Show Content and Download Button ---
if st.session_state['generated_content']:
    st.markdown("### Preview")
    st.write(st.session_state['generated_content'])
    
    # Create the file for download
    docx_file = create_docx(st.session_state['generated_content'])
    
    st.download_button(
        label="📥 Download as Word Document",
        data=docx_file,
        file_name=f"{mode.replace(' ', '_')}.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )            
