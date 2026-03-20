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
        width: 100%; border-radius: 25px; 
        background-color: #1E88E5; color: white; 
        height: 3.5em; font-weight: bold; border: none;
    }
    .footer {
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #f1f1f1; color: #555;
        text-align: center; padding: 10px; font-size: 14px;
        border-top: 1px solid #e0e0e0; z-index: 100;
    }
    .stSelectbox [data-testid='stMarkdownContainer'] { font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. 2026 NIGERIAN CURRICULUM DATA ---
LEVELS = {
    "Pre-Nursery/Nursery": [
        "Letter Work (Literacy)", "Number Work (Numeracy)", "Science Experience", 
        "Health Habits", "Social Norms", "Creative Arts", "Rhymes & Poems"
    ],
    "Lower Primary (1-3)": [
        "English Studies", "Mathematics", "Nigerian Language (Hausa/Igbo/Yoruba)", 
        "Basic Science", "Physical & Health Education", "Religious Studies (CRS/IS)", 
        "Nigerian History", "Social & Citizenship Studies", "Cultural & Creative Arts (CCA)"
    ],
    "Upper Primary (4-6)": [
        "English Studies", "Mathematics", "Nigerian Language", "Basic Science & Tech", 
        "Physical & Health Education", "Basic Digital Literacy", "Religious Studies", 
        "Nigerian History", "Social & Citizenship Studies", "Cultural & Creative Arts", 
        "Pre-Vocational Studies", "French"
    ],
    "Junior Secondary (JSS 1-3)": [
        "English Studies", "Mathematics", "Intermediate Science", "Digital Technologies", 
        "Nigerian History", "Social & Citizenship Studies", "Physical & Health Ed.", 
        "Business Studies", "Cultural & Creative Arts", "Religious Studies",
        "Trade Subject"
    ],
    "Senior Secondary (SSS 1-3)": [
        "General Mathematics (Core)", "English Language (Core)", "Citizenship & Heritage Studies (Core)", 
        "Digital Technologies (Core)", "Biology", "Chemistry", "Physics", "Further Mathematics", 
        "Agricultural Science", "Economics", "Government", "Literature-in-English", 
        "Geography", "Accounting", "Commerce", "Marketing", "Trade Subject"
    ]
}

# --- 3. LOGIC & EXPORT ---
try:
    api_key = st.secrets["GROQ_API_KEY"]
    client = Groq(api_key=api_key)
except Exception:
    st.error("🔑 API Key Missing! Check your Streamlit Secrets.")
    st.stop()

def create_docx(text, title):
    doc = Document()
    doc.add_heading(f'VIKIDYL AI: {title}', 0)
    clean_text = text.replace('$', '').replace('\\', '') 
    doc.add_paragraph(clean_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. THE INTERFACE ---
st.title("🎓 VIKIDYL AI")
st.caption("Customized for the New Nigerian Curriculum Standards")

tabs = st.tabs(["📚 Lesson Notes", "📊 Exams & Tests"])

with tabs[0]:
    st.subheader("Scripted 5-Step Lesson")
    
    c_level, c_tone = st.columns(2)
    with c_level:
        cat = st.selectbox("School Level", list(LEVELS.keys()))
    with c_tone:
        # NEW: TONE SELECTOR
        tone = st.selectbox("Teaching Tone", ["Playful & Story-based", "Inquiry-based (Active)", "Formal & Academic", "Exam-Focused"])
    
    sub = st.selectbox("Subject", LEVELS[cat])
    
    col_t, col_g = st.columns(2)
    topic = col_t.text_input("Topic", placeholder="e.g. My Body Parts")
    grade = col_g.text_input("Class", placeholder="e.g. Nursery 1")
    
    if st.button("Generate Scripted Lesson"):
        if topic:
            prompt = f"""As an expert {sub} teacher for {cat}, create a 5-step script for {topic}, {grade}. 
            TONE: {tone}.
            STRUCTURE: 
            1. Hook/Anticipatory Set
            2. Instruction (Scripted)
            3. Guided Practice
            4. Independent Practice/Classwork
            5. Clear Student Note for copying.
            
            Format using 'Teacher Says:' and 'Write on Board:'. Use LaTeX for math."""
            
            with st.spinner(f"VIKIDYL AI is drafting your {tone} lesson..."):
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": f"You are VIKIDYL AI, a specialist in {cat} education and {sub}."},
                              {"role": "user", "content": prompt}]
                )
                st.session_state['output'] = chat.choices[0].message.content
                st.session_state['current_title'] = f"{sub} - {topic}"

with tabs[1]:
    st.subheader("Assessment Builder")
    cat_e = st.selectbox("Level", list(LEVELS.keys()), key="ce")
    sub_e = st.selectbox("Subject", LEVELS[cat_e], key="se")
    
    c1, c2 = st.columns(2)
    objs = c1.number_input("Objective Questions", 5, 60, 20)
    theory = c2.number_input("Theory Questions", 1, 10, 5)
    scheme = st.text_area("List Topics from Scheme of Work")

    if st.button("Set Examination Paper"):
        prompt = f"Create a {sub_e} exam for {cat_e}. {objs} MCQs, {theory} Theory questions. Include Answer Key. Topics: {scheme}."
        with st.spinner("VIKIDYL AI is setting the paper..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are VIKIDYL AI, an expert Nigerian Examination Officer."},
                          {"role": "user", "content": prompt}]
                )
            st.session_state['output'] = chat.choices[0].message.content
            st.session_state['current_title'] = f"{sub_e} Exam"

# --- 5. OUTPUT ---
if 'output' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['output'])
    file = create_docx(st.session_state['output'], st.session_state.get('current_title', 'Material'))
    st.download_button("📥 Download Official Word Document", file, "VIKIDYL_AI_Note.docx")

# --- 6. FOOTER ---
st.markdown("""
    <div style="height: 100px;"></div>
    <div class="footer">
        <p>Developed by <b>Ufford I. I.</b> | Contact: <a href="mailto:your@email.com">digitalisedmindset@gmail.com</a><br>
        © 2026 VIKIDYL AI - Quality Education Standards</p>
    </div>
    """, unsafe_allow_html=True)
