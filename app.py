import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="Chalkie AI Pro", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #2E7D32; color: white; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE SECRET CONNECTION ---
# This looks for "GROQ_API_KEY" inside the Streamlit Secrets box you saw earlier.
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception as e:
    st.error("🔑 API Key Missing! Go to App Settings -> Secrets and add: GROQ_API_KEY = 'your_key_here'")
    st.stop()

# --- 3. DOCUMENT EXPORTER ---
def create_docx(text):
    doc = Document()
    doc.add_heading('Official Academic Material', 0)
    clean_text = text.replace('$', '') # Clean math symbols for Word
    doc.add_paragraph(clean_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. THE INTERFACE ---
st.title("🎓 Chalkie AI: Master Planner")
st.write("Generate professional, ready-to-use lesson scripts and exams.")

tabs = st.tabs(["📝 Lesson Notes", "📊 Exams & Tests"])

with tabs[0]:
    st.subheader("Scripted 5-Step Lesson")
    topic = st.text_input("Topic", placeholder="e.g. Photosynthesis")
    grade = st.text_input("Grade", placeholder="e.g. Primary 5")
    
    if st.button("Generate Full Lesson Script"):
        prompt = f"Create a detailed 5-step lesson script (Hook, Instruction, Examples, Classwork, Student Note) for {topic}, Grade {grade}. Use 'Teacher Says:' and 'Write on Board:'. Use LaTeX for math."
        with st.spinner("Writing your script..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are a Master Teacher. Provide ready-to-use classroom scripts."},
                          {"role": "user", "content": prompt}]
            )
            st.session_state['output'] = chat.choices[0].message.content

with tabs[1]:
    st.subheader("Custom Exam Builder")
    weeks = st.text_input("Period Covered", placeholder="e.g. Weeks 1-4")
    c1, c2 = st.columns(2)
    objs = c1.number_input("Objective Questions", 5, 50, 10)
    theory = c2.number_input("Theory Questions", 1, 10, 3)
    scheme = st.text_area("Paste Scheme of Work Topics")

    if st.button("Generate Examination Paper"):
        prompt = f"Create an exam for {weeks}. Include {objs} MCQs and {theory} theory questions with an answer key. Base on: {scheme}. Use LaTeX for math."
        with st.spinner("Generating exam..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are an Examination Officer."},
                          {"role": "user", "content": prompt}]
            )
            st.session_state['output'] = chat.choices[0].message.content

# --- 5. RESULTS & DOWNLOAD ---
if 'output' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['output'])
    
    file_data = create_docx(st.session_state['output'])
    st.download_button(
        label="📥 Download Word Document",
        data=file_data,
        file_name="Chalkie_Material.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
