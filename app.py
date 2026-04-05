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

# --- 2. PRE-LISTED SUBJECT DATA ---
DATA = {
    "Pre-Nursery/Nursery": ["Letter Work", "Number Work", "Health Habits", "Social Norms", "Rhymes", "Creative Arts", "Science Experience"],
    "Primary (Basic 1-6)": ["Mathematics", "English Studies", "Basic Science & Tech", "Social Studies", "Nigerian History", "P.H.E", "Agriculture", "Home Economics", "Cultural Arts"],
    "Junior College (JSS 1-3)": ["Mathematics", "English", "Basic Science", "Basic Technology", "Business Studies", "Social Studies", "Civic Education", "Agricultural Science", "Home Economics"],
    "Senior College (SSS 1-3)": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Further Maths", "Economics", "Government", "Literature", "Geography", "Commerce", "Financial Accounting"]
}

# --- 3. CONNECTION & HELPERS ---
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
st.title("🎓 VIKIDYL AI: Professional Suite")
st.caption("2026 NERDC Standard • Serialized 3-Term Curriculum")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessment Builder", "📅 NERDC Scheme & Detailed Notes"])

# --- TAB 1: QUICK TOOLS ---
with tabs[0]:
    st.subheader("Fast Lesson Script")
    q_lvl = st.selectbox("School Level", list(DATA.keys()), key="q_lvl")
    q_sub = st.selectbox("Subject", DATA[q_lvl], key="q_sub")
    q_top = st.text_input("Specific Topic", key="q_top")
    if st.button("Generate Script"):
        prompt = f"Quick 5-step script for {q_lvl} {q_sub}: {q_top}. Include Teacher Says and Write on Board."
        with st.spinner("Writing..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['out'] = chat.choices[0].message.content

# --- TAB 2: ASSESSMENT BUILDER ---
with tabs[1]:
    st.subheader("Test & Exam Moderator")
    col1, col2 = st.columns(2)
    a_lvl = col1.selectbox("Level", list(DATA.keys()), key="a_lvl")
    a_sub = col2.selectbox("Subject", DATA[a_lvl], key="a_sub")
    
    # MODERATION SELECTOR
    a_mode = st.select_slider("Moderation Style", options=["Fun & Engaging", "Balanced", "Serious Academic", "Strict Exam Mode"])
    a_top = st.text_area("Topics to cover")
    
    if st.button("Generate Moderated Assessment"):
        prompt = f"Generate a {a_mode} style exam for {a_lvl} {a_sub}. Topics: {a_top}. Include MCQs, Theory, and Answer Key."
        with st.spinner(f"Setting {a_mode} questions..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['out'] = chat.choices[0].message.content

# --- TAB 3: SCHEME & DETAILED NOTES ---
with tabs[2]:
    st.subheader("Full Serialized Planner")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        f_lvl = st.selectbox("School Level", list(DATA.keys()), key="f_lvl")
        f_sub = st.selectbox("Subject", DATA[f_lvl], key="f_sub")
        f_mod = st.radio("Action", ["Generate Full 3-Term Serialized Scheme", "Generate Detailed Weekly Lesson Note"])
    
    with c2:
        st.write("📂 **Reference Upload (Optional Override)**")
        st.file_uploader("Upload Scheme Image", type=["jpg", "png", "pdf"])
        st.text_area("Paste Custom Topics here", height=70, key="manual_ref")

    if f_mod == "Generate Detailed Weekly Lesson Note":
        st.write("---")
        n1, n2 = st.columns(2)
        f_trm = n1.selectbox("Term", ["1st Term", "2nd Term", "3rd Term"])
        f_wk = n2.selectbox("Week", [f"Week {i}" for i in range(1, 13)])
        f_top = st.text_input("Enter Topic Name")

    if st.button("🚀 Process NERDC Material"):
        if f_mod == "Generate Full 3-Term Serialized Scheme":
            prompt = f"Create a serialized 3-term scheme for {f_lvl} {f_sub}. List as: 1st Term (Week 1-12), 2nd Term (Week 1-12), 3rd Term (Week 1-12). Include Topics and Objectives."
        else:
            prompt = f"""Write a comprehensive NERDC Lesson Note for {f_lvl}, {f_sub}.
            TERM: {f_trm} | WEEK: {f_wk} | TOPIC: {f_top}.
            
            FOLLOW THIS 18-POINT OUTLINE:
            1. Subject, 2. Date, 3. Class, 4. Duration, 5. Age, 6. Gender, 7. Theme, 8. Learning Outcome, 9. Focal Competence, 10. Topic, 11. Performance Objectives, 12. Teaching Resources, 13. Previous Knowledge.
            14. PRESENTATION IN STEPS (Detailed Teacher/Pupil Activities).
            15. WORKED EXAMPLES WITH FULL SOLUTIONS.
            16. CLASSWORK & HOMEWORK (Minimum 5 questions each).
            17. EVALUATION & CONCLUSION.
            18. FULL STUDENT NOTE (Detailed enough for their notebooks).
            """
        
        with st.spinner("AI is generating professional content..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['out'] = chat.choices[0].message.content

# --- 5. RESULTS ---
if 'out' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['out'])
    
    f_data = create_docx(st.session_state['out'], "VIKIDYL_AI_Output")
    col_d, col_c = st.columns(2)
    col_d.download_button("📥 Download Official Word Doc", f_data, "VIKIDYL_AI.docx")
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
