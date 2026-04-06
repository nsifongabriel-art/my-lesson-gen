import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO
import re

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="VIKIDYL AI Pro", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #1E88E5; color: white; height: 3.5em; font-weight: bold; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f1f1; text-align: center; padding: 10px; font-size: 14px; border-top: 1px solid #e0e0e0; z-index: 99; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. THE MATH FIXER (FOR WORD DOCUMENTS) ---
def clean_math_for_word(text):
    """Converts LaTeX symbols to human-readable text for Word printing."""
    replacements = {
        r'\\frac\{(.+?)\}\{(.+?)\}': r'\1/\2',
        r'\\sqrt\{(.+?)\}': r'√( \1 )',
        r'\\text\{(.+?)\}': r'\1',
        r'\^2': '²', r'\^3': '³',
        r'\$': '', r'\\': ''
    }
    for pattern, replacement in replacements.items():
        text = re.sub(pattern, replacement, text)
    return text

# --- 3. DATA SEGMENTATION ---
CURRICULUM_DATA = {
    "Nursery": {
        "Classes": ["Pre-Nursery", "Nursery 1", "Nursery 2"],
        "Subjects": ["Letter Work", "Number Work", "Health Habits", "Social Norms", "Rhymes"]
    },
    "Primary": {
        "Classes": ["Basic 1", "Basic 2", "Basic 3", "Basic 4", "Basic 5", "Basic 6"],
        "Subjects": ["Mathematics", "English Studies", "Basic Science & Tech", "Social Studies", "P.H.E", "Agriculture"]
    },
    "Junior Secondary": {
        "Classes": ["JSS 1", "JSS 2", "JSS 3"],
        "Subjects": ["Mathematics", "English", "Basic Science", "Basic Technology", "Business Studies"]
    },
    "Senior Secondary": {
        "Classes": ["SSS 1", "SSS 2", "SSS 3"],
        "Subjects": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Further Maths", "Economics"]
    }
}

# --- 4. CONNECTION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing! Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

def create_docx(text, title):
    doc = Document()
    doc.add_heading(f'VIKIDYL AI - {title}', 0)
    # Applying the Math Fixer here
    final_text = clean_math_for_word(text)
    doc.add_paragraph(final_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 5. INTERFACE ---
st.title("🎓 VIKIDYL AI Professional")
st.caption("NERDC 2026 • Serialized Curriculum • Print-Ready Mathematics")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessment Builder", "📅 NERDC Scheme & Detailed Notes"])

# --- TAB 3: SCHEME & NOTES (The Core Tool) ---
with tabs[2]:
    st.subheader("Official Serialized Planner")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        lvl_f = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_f")
        cls_f = st.selectbox("Exact Class", CURRICULUM_DATA[lvl_f]["Classes"], key="cls_f")
        sub_f = st.selectbox("Subject", CURRICULUM_DATA[lvl_f]["Subjects"], key="sub_f")
        mode_f = st.radio("Action", ["Serialized 3-Term Scheme", "Comprehensive Weekly Lesson Note"])
    
    with c2:
        st.info("📎 Optional Reference Upload")
        st.file_uploader("Upload Image/PDF", type=["jpg", "png", "pdf"])
        manual_f = st.text_area("Paste Specific Topics (Optional Override)", height=70)

    if mode_f == "Comprehensive Weekly Lesson Note":
        st.write("---")
        n1, n2 = st.columns(2)
        trm_f = n1.selectbox("Term", ["1st Term", "2nd Term", "3rd Term"])
        wk_f = n2.selectbox("Select Week", [f"Week {i}" for i in range(1, 13)])
        top_f = st.text_input("Enter Weekly Topic")

    if st.button("🚀 Generate NERDC Material"):
        if mode_f == "Serialized 3-Term Scheme":
            prompt = f"Generate a year scheme for {cls_f} {sub_f}. List Term 1 (Wk 1-12), Term 2 (Wk 1-12), Term 3 (Wk 1-12). Use clean symbols."
        else:
            prompt = f"""Write a comprehensive Lesson Note for {cls_f}, {sub_f}. 
            TERM: {trm_f} | WEEK: {wk_f} | TOPIC: {top_f}.
            
            IMPORTANT: For all Math/Science symbols, use $...$ notation for screen rendering, but ensure they are easy to read. 
            Include 18-point outline: Subject, Theme, Learning Outcome, Focal Competence, etc. 
            Include 3 Worked Examples with full solutions and 5 Classwork/Homework questions.
            """
        with st.spinner("Processing..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['out'] = chat.choices[0].message.content
            st.session_state['t'] = f"{cls_f}_{sub_f}_Note"

# --- 6. RESULTS & EXPORT ---
if 'out' in st.session_state:
    st.markdown("---")
    # THE SCREEN RENDERER: This handles the math symbols for the teacher's eyes
    st.markdown(st.session_state['out'])
    
    file = create_docx(st.session_state['out'], st.session_state.get('t', 'Output'))
    col_d, col_c = st.columns(2)
    col_d.download_button("📥 Download Print-Ready Word Doc", file, f"{st.session_state.get('t', 'Doc')}.docx")
    if col_c.button("🗑️ Reset Page"):
        del st.session_state['out']
        st.rerun()

# --- FOOTER ---
st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="footer"><p>© 2026 VIKIDYL AI - Nigerian Education Standard</p></div>
    """, unsafe_allow_html=True)
