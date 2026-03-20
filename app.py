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
        box-shadow: 0px 4px 10px rgba(0,0,0,0.1);
    }
    .stButton>button:hover { background-color: #1565C0; color: white; }
    h1 { color: #1E88E5; font-family: 'Helvetica Neue', sans-serif; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE SECRET CONNECTION ---
try:
    # This pulls from the Secrets box you updated
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception as e:
    st.error("🔑 API Key Missing! Please add it to your Streamlit App Secrets.")
    st.stop()

# --- 3. DOCUMENT EXPORTER ---
def create_docx(text):
    doc = Document()
    doc.add_heading('VIKIDYL AI - Official Academic Material', 0)
    # Removing LaTeX symbols for better Word compatibility
    clean_text = text.replace('$', '').replace('\\', '') 
    doc.add_paragraph(clean_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. THE INTERFACE ---
st.title("🎓 VIKIDYL AI")
st.write("The intelligent assistant for modern educators. Generate scripts, notes, and assessments in seconds.")

tabs = st.tabs(["📚 Lesson Notes", "📊 Exams & Tests"])

with tabs[0]:
    st.subheader("Scripted 5-Step Lesson")
    topic = st.text_input("What topic are we teaching today?", placeholder="e.g. Quadratic Equations")
    grade = st.text_input("Grade Level", placeholder="e.g. SSS 2")
    
    if st.button("Generate VIKIDYL Lesson Script"):
        prompt = f"Create a detailed 5-step lesson script (Hook, Instruction, Examples, Classwork, Student Note) for {topic}, Grade {grade}. Use 'Teacher Says:' and 'Write on Board:'. Use LaTeX for math symbols."
        with st.spinner("VIKIDYL AI is drafting your lesson..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are VIKIDYL AI, a Master Education Consultant. Provide ready-to-use classroom scripts with clear student notes."},
                          {"role : "user", "content": prompt}]
            )
            st.session_state['output'] = chat.choices[0].message.content

with tabs[1]:
    st.subheader("Custom Exam Builder")
    weeks = st.text_input("Weeks/Period Covered", placeholder="e.g. Mid-Term (Weeks 1-6)")
    c1, c2 = st.columns(2)
    objs = c1.number_input("Objective Questions", 5, 100, 20)
    theory = c2.number_input("Theory Questions", 1, 20, 5)
    scheme = st.text_area("Paste Scheme of Work / Topics here")

    if st.button("Generate VIKIDYL Examination"):
        prompt = f"Create an exam for {weeks}. Include {objs} MCQs and {theory} theory questions with an answer key. Base it on these topics: {scheme}. Use LaTeX for math."
        with st.spinner("VIKIDYL AI is setting the questions..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are VIKIDYL AI, an expert Examination Officer."},
                          {"role": "user", "content": prompt}]
            )
            st.session_state['output'] = chat.choices[0].message.content

# --- 5. RESULTS & DOWNLOAD ---
if 'output' in st.session_state:
    st.markdown("---")
    # Display on screen (renders LaTeX math)
    st.markdown(st.session_state['output'])
    
    file_data = create_docx(st.session_state['output'])
    st.download_button(
        label="📥 Download as Word Document",
        data=file_data,
        file_name="VIKIDYL_Material.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
