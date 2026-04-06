import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="VIKIDYL AI Pro", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #1E88E5; color: white; height: 3.5em; font-weight: bold; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f1f1; text-align: center; padding: 10px; font-size: 14px; border-top: 1px solid #e0e0e0; z-index: 99; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. INTEGRATED DATABASE (Level -> Class -> Subject) ---
CURRICULUM_DATA = {
    "Nursery": {
        "Classes": ["Pre-Nursery", "Nursery 1", "Nursery 2"],
        "Subjects": ["Letter Work", "Number Work", "Health Habits", "Social Norms", "Rhymes", "Creative Arts", "Science Experience"]
    },
    "Primary": {
        "Classes": ["Basic 1", "Basic 2", "Basic 3", "Basic 4", "Basic 5", "Basic 6"],
        "Subjects": ["Mathematics", "English Studies", "Basic Science & Tech", "Social Studies", "Nigerian History", "P.H.E", "Agriculture", "Home Economics", "Cultural & Creative Arts"]
    },
    "Junior Secondary": {
        "Classes": ["JSS 1", "JSS 2", "JSS 3"],
        "Subjects": ["Mathematics", "English", "Basic Science", "Basic Technology", "Business Studies", "Civic Education", "Agricultural Science", "Social Studies", "Home Economics"]
    },
    "Senior Secondary": {
        "Classes": ["SSS 1", "SSS 2", "SSS 3"],
        "Subjects": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Further Maths", "Economics", "Government", "Literature", "Geography", "Commerce", "Financial Accounting", "Civic Education"]
    }
}

# --- 3. CONNECTION ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing! Please add GROQ_API_KEY to Streamlit Secrets.")
    st.stop()

def create_docx(text, title):
    doc = Document()
    doc.add_heading(f'VIKIDYL AI - {title}', 0)
    # Removing LaTeX delimiters for clean printing in Word
    clean_text = text.replace('$', '').replace('\\', '') 
    doc.add_paragraph(clean_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. THE INTERFACE ---
st.title("🎓 VIKIDYL AI Professional")
st.caption("NERDC 2026 Standards • Class-Specific Intelligence • Print-Ready Math")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessment Builder", "📅 NERDC Scheme & Detailed Notes"])

# --- TAB 1: QUICK TOOLS ---
with tabs[0]:
    st.subheader("Fast Lesson Script")
    lvl_q = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_q")
    cls_q = st.selectbox("Exact Class", CURRICULUM_DATA[lvl_q]["Classes"], key="cls_q")
    sub_q = st.selectbox("Subject", CURRICULUM_DATA[lvl_q]["Subjects"], key="sub_q")
    top_q = st.text_input("Topic", placeholder="Enter topic here...", key="top_q")
    
    if st.button("Generate Quick Script"):
        if top_q:
            with st.spinner("Writing script..."):
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Write a quick 5-step lesson script for {cls_q} {sub_q}: {top_q}. Use 'Teacher Says' and 'Write on Board'."}]
                )
                st.session_state['out'] = chat.choices[0].message.content
                st.session_state['t'] = f"QuickScript_{cls_q}_{sub_q}"

# --- TAB 2: ASSESSMENT BUILDER ---
with tabs[1]:
    st.subheader("Moderated Test & Exam Generator")
    col1, col2 = st.columns(2)
    lvl_a = col1.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_a")
    cls_a = col2.selectbox("Exact Class", CURRICULUM_DATA[lvl_a]["Classes"], key="cls_a")
    sub_a = st.selectbox("Subject", CURRICULUM_DATA[lvl_a]["Subjects"], key="sub_a")
    
    # MODERATION SLIDER
    mod_a = st.select_slider("Assessment Moderation Style", 
                            options=["Fun & Practical", "Standard Classroom", "Serious Academic", "Strict External Exam Style"])
    
    top_a = st.text_area("List Topics for Assessment (From Scheme of Work)")
    
    if st.button("Generate Moderated Exam"):
        if top_a:
            prompt = f"Create a {mod_a} style exam for {cls_a} {sub_a}. Topics: {top_a}. Render all math/science notations in clear LaTeX ($...$). Include MCQs, Theory, and Answer Key."
            with st.spinner(f"Setting {mod_a} questions..."):
                chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state['out'] = chat.choices[0].message.content
                st.session_state['t'] = f"Exam_{cls_a}_{sub_a}"

# --- TAB 3: SCHEME & NOTES ---
with tabs[2]:
    st.subheader("Official Serialized Planner")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        lvl_f = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_f")
        cls_f = st.selectbox("Exact Class", CURRICULUM_DATA[lvl_f]["Classes"], key="cls_f")
        sub_f = st.selectbox("Subject", CURRICULUM_DATA[lvl_f]["Subjects"], key="sub_f")
        mode_f = st.radio("Action", ["Serialized 3-Term Scheme (Full Year)", "Comprehensive Weekly Lesson Note"])
    
    with c2:
        st.info("📎 Optional: Reference your own specific scheme.")
        st.file_uploader("Upload Image/PDF", type=["jpg", "png", "pdf"])
        manual_f = st.text_area("Paste Specific Topics (Optional Override)", height=70)

    if mode_f == "Comprehensive Weekly Lesson Note":
        st.write("---")
        n1, n2 = st.columns(2)
        trm_f = n1.selectbox("Term", ["1st Term", "2nd Term", "3rd Term"])
        wk_f = n2.selectbox("Select Week", [f"Week {i}" for i in range(1, 13)])
        top_f = st.text_input("Enter Weekly Topic")

    if st.button("🚀 Generate NERDC Material"):
        ref_context = f"Override using this: {manual_f}" if manual_f else "Use official NERDC curriculum."
        
        if mode_f == "Serialized 3-Term Scheme (Full Year)":
            prompt = f"Generate a serialized 3-term scheme for {cls_f} {sub_f}. {ref_context} List 1st Term (Week 1-12), 2nd Term (Week 1-12), and 3rd Term (Week 1-12) with topics and objectives. Use proper math/science notation."
        else:
            prompt = f"""Write a comprehensive NERDC Lesson Note for {cls_f}, {sub_f}.
            TERM: {trm_f} | WEEK: {wk_f} | TOPIC: {top_f}. {ref_context}
            
            STRUCTURE (18 POINTS):
            1. Subject, 2. Date, 3. Class, 4. Duration, 5. Age, 6. Gender, 7. Theme, 8. Learning Outcome, 9. Focal Competence, 10. Topic, 11. Performance Objectives, 12. Teaching Resources, 13. Previous Knowledge.
            14. PRESENTATION: Detailed Teacher vs Pupil Activities.
            15. WORKED EXAMPLES: Detailed examples with full step-by-step solutions (use LaTeX math symbols).
            16. CLASSWORK & HOMEWORK: Specific practice questions.
            17. EVALUATION & CONCLUSION.
            18. FULL STUDENT NOTE: Comprehensive note for copying.
            """
        with st.spinner("Processing..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['out'] = chat.choices[0].message.content
            st.session_state['t'] = f"Note_{cls_f}_{sub_f}"

# --- 5. RESULTS & EXPORT ---
if 'out' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['out'])
    
    file = create_docx(st.session_state['out'], st.session_state.get('t', 'Output'))
    col_d, col_c = st.columns(2)
    col_d.download_button("📥 Download Official Word Doc", file, f"{st.session_state['t']}.docx")
    if col_c.button("🗑️ Reset Page"):
        del st.session_state['out']
        st.rerun()

# --- 6. FOOTER ---
# Remember to update the email below
st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="footer">
        <p>Developed by <b>Ufford I. I. -Vikidyl Consult</b> | Support: <a href="mailto:digitalisedmindset@gmail.com">your@email.com</a><br>
        © 2026 VIKIDYL AI - Nigerian Education Standard</p>
    </div>
    """, unsafe_allow_html=True)
