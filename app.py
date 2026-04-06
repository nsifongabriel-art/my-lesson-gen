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

# --- 2. MATH SYMBOL CLEANER ---
def format_math_for_print(text):
    subs = {
        r'\\frac\{(.+?)\}\{(.+?)\}': r'(\1 / \2)',
        r'\\sqrt\{(.+?)\}': r'√(\1)',
        r'\\pm': '±', r'\\times': '×', r'\\div': '÷',
        r'\^2': '²', r'\^3': '³', r'\$': '', r'\\': ''
    }
    for pattern, replacement in subs.items():
        text = re.sub(pattern, replacement, text)
    return text

# --- 3. CURRICULUM DATABASE ---
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

# --- 4. CONNECTION & UTILS ---
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
st.caption("NERDC 2026 Standards • Full 3-Term Serialized Planning")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessment Builder", "📅 NERDC Scheme & Notes"])

# --- TAB 1: QUICK TOOLS (RESTORED) ---
with tabs[0]:
    st.subheader("Fast Lesson Script")
    lvl_q = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_q")
    cls_q = st.selectbox("Exact Class", CURRICULUM_DATA[lvl_q]["Classes"], key="cls_q")
    sub_q = st.selectbox("Subject", CURRICULUM_DATA[lvl_q]["Subjects"], key="sub_q")
    top_q = st.text_input("Topic", placeholder="e.g. Addition of Fractions", key="top_q")
    
    if st.button("Generate Quick Script"):
        if top_q:
            prompt_q = f"Write a quick lesson script for {cls_q} {sub_q}: {top_q}. Focus on 'Teacher Says' and 'Write on Board'."
            with st.spinner("Drafting script..."):
                chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_q}])
                st.session_state['out'] = chat.choices[0].message.content
                st.session_state['t'] = f"QuickScript_{cls_q}_{sub_q}"

# --- TAB 2: ASSESSMENT BUILDER (RESTORED) ---
with tabs[1]:
    st.subheader("Automated Exam & Test Generator")
    lvl_a = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_a")
    cls_a = st.selectbox("Exact Class", CURRICULUM_DATA[lvl_a]["Classes"], key="cls_a")
    sub_a = st.selectbox("Subject", CURRICULUM_DATA[lvl_a]["Subjects"], key="sub_a")
    top_a = st.text_area("Topics to Cover", placeholder="List topics from your scheme...")
    
    if st.button("Generate Assessment"):
        if top_a:
            prompt_a = f"Create a standard assessment for {cls_a} {sub_a} based on these topics: {top_a}. Include MCQs and Theory with an Answer Key. Use printable math symbols."
            with st.spinner("Generating questions..."):
                chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt_a}])
                st.session_state['out'] = chat.choices[0].message.content
                st.session_state['t'] = f"Exam_{cls_a}_{sub_a}"

# --- TAB 3: NERDC SCHEME & NOTES (PRESERVED INTEGRITY) ---
with tabs[2]:
    st.subheader("Official Serialized Planner & Note Generator")
    col1, col2 = st.columns([1, 1])
    
    with col1:
        lvl_f = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_f")
        cls_f = st.selectbox("Exact Class", CURRICULUM_DATA[lvl_f]["Classes"], key="cls_f")
        sub_f = st.selectbox("Subject", CURRICULUM_DATA[lvl_f]["Subjects"], key="sub_f")
        trm_f = st.selectbox("Target Term", ["1st Term", "2nd Term", "3rd Term", "Full Year (All 3 Terms)"], key="trm_f")
    
    with col2:
        mode_f = st.radio("Action", ["Serialized Scheme (Week 1-12)", "Detailed Weekly Lesson Note"])
        manual_ref = st.text_area("Paste Specific Topics (Optional Override)", height=70)

    # Note-specific inputs
    wk_f, top_f = "N/A", "N/A"
    if mode_f == "Detailed Weekly Lesson Note":
        st.write("---")
        n1, n2 = st.columns(2)
        wk_f = n1.selectbox("Select Week", [f"Week {i}" for i in range(1, 13)])
        top_f = n2.text_input("Enter Topic Name")

    if st.button("🚀 Generate NERDC Material"):
        ref = f"Reference: {manual_ref}" if manual_ref else "Use standard NERDC 2026 curriculum."
        
        if mode_f == "Serialized Scheme (Week 1-12)":
            prompt_f = f"""Generate a serialized scheme of work for {cls_f} {sub_f} for {trm_f}. 
            CRITICAL: List Week 1, Week 2, Week 3... through Week 12 individually. 
            Do NOT combine weeks. For every single week, provide a Topic and Behavioral Objectives. {ref}"""
            st.session_state['t'] = f"{cls_f}_{sub_f}_{trm_f}_Scheme"
        else:
            prompt_f = f"""Write a comprehensive Lesson Note for {cls_f}, {sub_f}. TERM: {trm_f} | WEEK: {wk_f} | TOPIC: {top_f}. {ref}
            STRUCTURE (FOLLOW 18-POINT OUTLINE STRICTLY):
            1. Subject, 2. Date, 3. Class, 4. Duration, 5. Age, 6. Gender, 7. Theme, 8. Learning Outcome, 9. Focal Competence, 10. Topic, 11. Performance Objectives, 12. Teaching Resources, 13. Previous Knowledge.
            14. PRESENTATION: Detailed Step-by-Step Teacher vs Pupil Activities.
            15. WORKED EXAMPLES: Detailed examples with solutions using clear text math symbols.
            16. CLASS ACTIVITIES. 17. EVALUATION. 18. CONCLUSION/ASSIGNMENT.
            Include a FULL STUDENT NOTE at the end."""
            st.session_state['t'] = f"{cls_f}_{sub_f}_{wk_f}"

        with st.spinner("Generating accurate NERDC material..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "Expert Nigerian curriculum consultant. Never group weeks together. Use printable symbols (x/y, √, ^2)."},
                          {"role": "user", "content": prompt_f}]
            )
            st.session_state['out'] = chat.choices[0].message.content

# --- 6. RESULTS & FOOTER ---
if 'out' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['out'])
    file = create_docx(st.session_state['out'], st.session_state.get('t', 'Output'))
    c_d, c_c = st.columns(2)
    c_d.download_button("📥 Download Word Doc", file, f"{st.session_state.get('t', 'File')}.docx")
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
