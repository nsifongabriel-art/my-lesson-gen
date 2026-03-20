import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="VIKIDYL AI", page_icon="🎓", layout="centered")

st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .stButton>button { 
        width: 100%; 
        border-radius: 25px; 
        background-color: #1E88E5; 
        color: white; 
        height: 3.5em; 
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #1565C0; color: white; }
    h1 { color: #1E88E5; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE SECRET CONNECTION ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception as e:
    st.error("🔑 API Key Missing in Secrets!")
    st.stop()

# --- 3. DOCUMENT EXPORTER ---
def create_docx(text):
    doc = Document()
    doc.add_heading('VIKIDYL AI - Official Academic Material', 0)
    clean_text = text.replace('$', '').replace('\\', '') 
    doc.add_paragraph(clean_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. THE INTERFACE ---
st.title("🎓 VIKIDYL AI")
st.write("Intelligent assistance for modern educators.")

tabs = st.tabs(["📚 Lesson Notes", "📊 Exams & Tests"])

with tabs[0]:
    st.subheader("Scripted 5-Step Lesson")
    topic = st.text_input("Topic", placeholder="e.g. Fractions")
    grade = st.text_input("Grade", placeholder="e.g. JSS 1")
    
    if st.button("Generate VIKIDYL Lesson"):
        if not topic:
            st.warning("Please enter a topic!")
        else:
            prompt = f"Create a 5-step lesson script (Hook, Instruction, Examples, Classwork, Student Note) for {topic}, Grade {grade}. Use 'Teacher Says:' and 'Write on Board:'. Use LaTeX for math."
            with st.spinner("VIKIDYL AI is thinking..."):
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[
                        {"role": "system", "content": "You are VIKIDYL AI, a Master Education Consultant."},
                        {"role": "user", "content": prompt}
                    ]
                )
                st.session_state['output'] = chat.choices[0].message.content

with tabs[1]:
    st.subheader("Custom Exam Builder")
    weeks = st.text_input("Period", placeholder="e.g. Weeks 1-6")
    c1, c2 = st.columns(2)
    objs = c1.number_input("Objectives", 5, 100, 20)
    theory = c2.number_input("Theory", 1, 20, 5)
    scheme = st.text_area("Paste Topics")

    if st.button("Generate VIKIDYL Exam"):
        prompt = f"Create an exam for {weeks}. Include {objs} MCQs and {theory} theory questions. Answer key at end. Topics: {scheme}. Use LaTeX for math."
        with st.spinner("Setting questions..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": "You are VIKIDYL AI, an expert Examination Officer."},
                    {"role": "user", "content": prompt}
                ]
            )
            st.session_state['output'] = chat.choices[0].message.content

# --- 5. RESULTS & DOWNLOAD ---
if 'output' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['output'])
    
    file_data = create_docx(st.session_state['output'])
    st.download_button(
        label="📥 Download as Word Document",
        data=file_data,
        file_name="VIKIDYL_Material.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
