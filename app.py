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

# --- 2. MATH & SYMBOL CLEANER (FOR PRINT INTEGRITY) ---
def format_math_for_print(text):
    """Converts LaTeX code into clear, printable text symbols."""
    subs = {
        r'\\frac\{(.+?)\}\{(.+?)\}': r'(\1 / \2)',
        r'\\sqrt\{(.+?)\}': r'√(\1)',
        r'\\pm': '±', r'\\times': '×', r'\\div': '÷',
        r'\^2': '²', r'\^3': '³', r'\$': '', r'\\': ''
    }
    for pattern, replacement in subs.items():
        text = re.sub(pattern, replacement, text)
    return text

# --- 3. CLASS & SUBJECT DATABASE (SERIALIZED) ---
CURRICULUM_DATA = {
    "Nursery": {
        "Classes": ["Pre-Nursery", "Nursery 1", "Nursery 2"],
        "Subjects": ["Letter Work", "Number Work", "Health Habits", "Social Norms", "Rhymes", "Science Experience"]
    },
    "Primary": {
        "Classes": ["Basic 1", "Basic 2", "Basic 3", "Basic 4", "Basic 5", "Basic 6"],
        "Subjects": ["Mathematics", "English Studies", "Basic Science & Tech", "Social Studies", "Nigerian History", "P.H.E", "Agriculture", "Home Economics"]
    },
    "Junior Secondary": {
        "Classes": ["JSS 1", "JSS 2", "JSS 3"],
        "Subjects": ["Mathematics", "English", "Basic Science", "Basic Technology", "Business Studies", "Civic Education", "Social Studies"]
    },
    "Senior Secondary": {
        "Classes": ["SSS 1", "SSS 2", "SSS 3"],
        "Subjects": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Further Maths", "Economics", "Government", "Food and Nutrition", "Financial Accounting"]
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
    doc.add_paragraph(format_math_for_print(text))
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 5. INTERFACE ---
st.title("🎓 VIKIDYL AI Professional")
st.caption("NERDC 2026 Standards • Serialized 12-Week Planning")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessment Builder", "📅 NERDC Scheme & Detailed Notes"])

# --- TAB 3: SCHEME & NOTES ---
with tabs[2]:
    st.subheader("Official Serialized Planner & Note Generator")
    col_input, col_ref = st.columns([1, 1])
    
    with col_input:
        lvl = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_f")
        cls = st.selectbox("Exact Class", CURRICULUM_DATA[lvl]["Classes"], key="cls_f")
        sub = st.selectbox("Subject", CURRICULUM_DATA[lvl]["Subjects"], key="sub_f")
        mode = st.radio("Action", ["Full Serialized Termly Scheme (Week 1-12)", "Detailed Weekly Lesson Note"])
    
    with col_ref:
        st.info("📎 Optional: Reference your school's specific curriculum.")
        st.file_uploader("Upload Image/PDF", type=["jpg", "png", "pdf"])
        manual_ref = st.text_area("Paste Specific Topics (Optional Override)", height=70)

    if mode == "Detailed Weekly Lesson Note":
        st.write("---")
        n1, n2, n3 = st.columns(3)
        trm = n1.selectbox("Term", ["1st Term", "2nd Term", "3rd Term"])
        wk = n2.selectbox("Select Week", [f"Week {i}" for i in range(1, 13)])
        top = n3.text_input("Enter Topic Name")

    if st.button("🚀 Generate NERDC Material"):
        ref = f"Reference: {manual_ref}" if manual_ref else "Use standard NERDC 2026 curriculum."
        
        if mode == "Full Serialized Termly Scheme (Week 1-12)":
            prompt = f"""Generate a full serialized 12-week scheme of work for {cls} {sub}. 
            CRITICAL: List Week 1, Week 2, Week 3... all the way to Week 12 individually. 
            Do NOT combine weeks. For each week, provide the Topic and Behavioral Objectives. {ref}"""
        else:
            prompt = f"""Write a comprehensive Lesson Note for {cls}, {sub}.
            TERM: {trm} | WEEK: {wk} | TOPIC: {top}. {ref}
            
            STRUCTURE (FOLLOW 18-POINT OUTLINE STRICTLY):
            1. Subject, 2. Date, 3. Class, 4. Duration, 5. Age, 6. Gender, 7. Theme, 8. Learning Outcome, 9. Focal Competence, 10. Topic, 11. Performance Objectives, 12. Teaching and Learning Resources, 13. Previous Knowledge.
            14. PRESENTATION: Detailed Step-by-Step Teacher vs Pupil Activities.
            15. WORKED EXAMPLES: Detailed examples with solutions using clear text math symbols.
            16. CLASS ACTIVITIES (IF ANY).
            17. EVALUATION.
            18. CONCLUSION / ASSIGNMENT.
            Include a FULL STUDENT NOTE at the end. Use clear symbols like x/y, √x, x²."""

        with st.spinner("Processing..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Expert NERDC consultant. Never combine weeks. Use printable symbols."},
                          {"role": "user", "content": prompt}]
            )
            st.session_state['out'] = chat.choices[0].message.content
            st.session_state['t'] = f"{cls}_{sub}_{wk}"

# --- 6. RESULTS & FOOTER ---
if 'out' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['out'])
    file = create_docx(st.session_state['out'], st.session_state['t'])
    c_d, c_c = st.columns(2)
    c_d.download_button("📥 Download Word Doc", file, f"{st.session_state['t']}.docx")
    if c_c.button("🗑️ Reset"):
        del st.session_state['out']
        st.rerun()

st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="footer">
        <p>Developed by <b>Ufford I.I. - Vikidyl Models Consult</b><br>
        Email: <a href="mailto:digitalisedmindset@gmail.com">digitalisedmindset@gmail.com</a><br>
        © 2026 VIKIDYL AI - Nigerian Education Standards</p>
    </div>
    """, unsafe_allow_html=True)
