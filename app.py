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

# --- 2. DATA SEGMENTATION (BY EXACT CLASS) ---
# This dictionary now maps the Group -> Specific Class -> Subject List
CURRICULUM_DATA = {
    "Nursery": {
        "Classes": ["Pre-Nursery", "Nursery 1", "Nursery 2"],
        "Subjects": ["Letter Work", "Number Work", "Health Habits", "Social Norms", "Rhymes", "Creative Arts"]
    },
    "Primary": {
        "Classes": ["Basic 1", "Basic 2", "Basic 3", "Basic 4", "Basic 5", "Basic 6"],
        "Subjects": ["Mathematics", "English Studies", "Basic Science & Tech", "Social Studies", "Nigerian History", "P.H.E", "Agriculture", "Home Economics"]
    },
    "Junior Secondary": {
        "Classes": ["JSS 1", "JSS 2", "JSS 3"],
        "Subjects": ["Mathematics", "English", "Basic Science", "Basic Technology", "Business Studies", "Civic Education", "Agricultural Science"]
    },
    "Senior Secondary": {
        "Classes": ["SSS 1", "SSS 2", "SSS 3"],
        "Subjects": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Further Maths", "Economics", "Government", "Literature", "Geography", "Commerce", "Financial Accounting"]
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
    clean_text = text.replace('$', '').replace('\\', '') 
    doc.add_paragraph(clean_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- 4. THE INTERFACE ---
st.title("🎓 VIKIDYL AI Professional")
st.caption("2026 NERDC Standard • Class-Specific Serialization")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessment Builder", "📅 NERDC Scheme & Detailed Notes"])

# --- TAB 1: QUICK TOOLS ---
with tabs[0]:
    st.subheader("Fast Lesson Script")
    lvl_q = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_q")
    cls_q = st.selectbox("Exact Class", CURRICULUM_DATA[lvl_q]["Classes"], key="cls_q")
    sub_q = st.selectbox("Subject", CURRICULUM_DATA[lvl_q]["Subjects"], key="sub_q")
    top_q = st.text_input("Topic", key="top_q")
    if st.button("Generate Quick Script"):
        with st.spinner("Processing..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Quick 5-step script for {cls_q} {sub_q}: {top_q}."}]
            )
            st.session_state['out'] = chat.choices[0].message.content

# --- TAB 2: ASSESSMENT BUILDER ---
with tabs[1]:
    st.subheader("Test & Exam Moderator")
    col1, col2 = st.columns(2)
    lvl_a = col1.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_a")
    cls_a = col2.selectbox("Exact Class", CURRICULUM_DATA[lvl_a]["Classes"], key="cls_a")
    sub_a = st.selectbox("Subject", CURRICULUM_DATA[lvl_a]["Subjects"], key="sub_a")
    
    mod_a = st.select_slider("Select Exam Tone/Moderation", 
                            options=["Fun & Practical", "Standard Classroom", "Serious Academic", "Strict External Exam Style"])
    
    top_a = st.text_area("List Topics for Assessment")
    if st.button("Generate Moderated Exam"):
        prompt = f"Create a {mod_a} style exam for {cls_a} {sub_a}. Topics: {top_a}. Include MCQs and Theory with solutions."
        with st.spinner(f"Setting {mod_a} questions..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['out'] = chat.choices[0].message.content

# --- TAB 3: SCHEME & NOTES (SERIALIZED BY CLASS) ---
with tabs[2]:
    st.subheader("Class-Specific Serialized Planner")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        lvl_f = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_f")
        cls_f = st.selectbox("Exact Class", CURRICULUM_DATA[lvl_f]["Classes"], key="cls_f")
        sub_f = st.selectbox("Subject", CURRICULUM_DATA[lvl_f]["Subjects"], key="sub_f")
        mode_f = st.radio("Action", ["Serialized 3-Term Scheme for this Class", "Detailed Weekly Lesson Note"])
    
    with c2:
        st.info("📎 Override standard NERDC by uploading your own scheme.")
        st.file_uploader("Upload Image/PDF", type=["jpg", "png", "pdf"])
        manual_f = st.text_area("Paste Specific Topics (Optional Override)", height=70)

    if mode_f == "Detailed Weekly Lesson Note":
        st.write("---")
        n1, n2 = st.columns(2)
        trm_f = n1.selectbox("Term", ["1st Term", "2nd Term", "3rd Term"])
        wk_f = n2.selectbox("Select Week", [f"Week {i}" for i in range(1, 13)])
        top_f = st.text_input("Enter Topic Name")

    if st.button("🚀 Generate Material"):
        if mode_f == "Serialized 3-Term Scheme for this Class":
            prompt = f"Generate a full year serialized scheme of work EXCLUSIVELY for {cls_f} {sub_f}. Do not mix with other classes. List Week 1-12 for 1st Term, Week 1-12 for 2nd Term, and Week 1-12 for 3rd Term separately with Topics and Behavioral Objectives."
        else:
            prompt = f"""Write a comprehensive Lesson Note for {cls_f}, {sub_f}.
            TERM: {trm_f} | WEEK: {wk_f} | TOPIC: {top_f}.
            
            STRUCTURE (FOLLOW STRICTLY):
            1-13. Subject, Date, Class, Duration, Age, Gender, Theme, Learning Outcome, Focal Competence, Topic, Performance Objectives, Teaching Resources, Previous Knowledge.
            14. PRESENTATION: Detailed Step-by-Step Teacher vs Pupil Activities.
            15. WORKED EXAMPLES: Detailed examples with full step-by-step solutions.
            16. CLASSWORK & HOMEWORK: Specific practice questions.
            17. EVALUATION & CONCLUSION.
            18. FULL STUDENT NOTE: Detailed for notebook copying.
            """
        with st.spinner(f"Generating for {cls_f}..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['out'] = chat.choices[0].message.content

# --- 5. RESULTS & EXPORT ---
if 'out' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['out'])
    
    file = create_docx(st.session_state['out'], "VIKIDYL_Document")
    col_d, col_c = st.columns(2)
    col_d.download_button("📥 Download Official Word Doc", file, "VIKIDYL_AI.docx")
    if col_c.button("🗑️ Reset Page"):
        del st.session_state['out']
        st.rerun()

# --- 6. FOOTER ---
st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="footer">
        <p>Developed by <b>Your Name</b> | Support: <a href="mailto:your@email.com">your@email.com</a><br>
        © 2026 VIKIDYL AI - Nigerian Education Standard</p>
    </div>
    """, unsafe_allow_html=True)
