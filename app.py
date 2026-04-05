import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="VIKIDYL AI Pro", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #1E88E5; color: white; height: 3.5em; font-weight: bold; border: none; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f1f1; text-align: center; padding: 10px; font-size: 14px; border-top: 1px solid #e0e0e0; z-index: 99; }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
CLASSES = ["Pre-Nursery", "Nursery 1", "Nursery 2", "Primary 1", "Primary 2", "Primary 3", "Primary 4", "Primary 5", "Primary 6", "JSS 1", "JSS 2", "JSS 3", "SSS 1", "SSS 2", "SSS 3"]
TERMS = ["1st Term", "2nd Term", "3rd Term"]

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
st.caption("Official NERDC Curriculum Suite (Pre-Nursery to Senior Secondary)")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessments", "📅 Full NERDC Scheme & Notes"])

# --- TAB 1: QUICK TOOLS ---
with tabs[0]:
    st.subheader("Fast 5-Step Lesson Script")
    col1, col2 = st.columns(2)
    q_cls = col1.selectbox("Class", CLASSES, key="q_cls")
    q_sub = st.text_input("Subject/Topic", key="q_sub")
    if st.button("Generate Quick Script", key="q_btn"):
        with st.spinner("Writing..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Quick 5-step lesson for {q_cls} on {q_sub}."}]
            )
            st.session_state['out'] = chat.choices[0].message.content
            st.session_state['t'] = f"Quick_{q_sub}"

# --- TAB 2: ASSESSMENT ---
with tabs[1]:
    st.subheader("Assessment Builder")
    col3, col4 = st.columns(2)
    a_cls = col3.selectbox("Class", CLASSES, key="a_cls")
    a_sub = col4.text_input("Subject", key="a_sub")
    a_ref = st.text_area("Reference Topics (from Scheme)", key="a_ref")
    if st.button("Generate Exam", key="a_btn"):
        with st.spinner("Setting questions..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Generate exam for {a_cls} {a_sub} based on: {a_ref}. Include MCQs and Theory."}]
            )
            st.session_state['out'] = chat.choices[0].message.content
            st.session_state['t'] = f"Exam_{a_sub}"

# --- TAB 3: FULL NERDC SCHEME & NOTES ---
with tabs[2]:
    st.subheader("Official Weekly Planner & Note Generator")
    c_set, c_ref = st.columns([1, 1])
    
    with c_set:
        f_cls = st.selectbox("Class", CLASSES, key="f_cls")
        f_trm = st.selectbox("Term", TERMS, key="f_trm")
        f_sub = st.text_input("Subject", key="f_sub")
    
    with c_ref:
        st.write("📖 **Reference Source**")
        upload = st.file_uploader("Upload Scheme (Optional)", type=["jpg", "png", "pdf"])
        manual_ref = st.text_area("Paste Specific Scheme Topics (Optional Override)", height=68)

    f_mod = st.radio("Action", ["Divide Curriculum into 3 Terms (Weekly Scheme)", "Generate Comprehensive Lesson Note"], key="f_mod")
    
    if f_mod == "Generate Comprehensive Lesson Note":
        f_wk = st.number_input("Week", 1, 12, 1)
        f_top = st.text_input("Weekly Topic")

    if st.button("🚀 Generate Material", key="f_btn"):
        ref_context = f"Use this user-provided scheme: {manual_ref}" if manual_ref else "Use the official National NERDC Curriculum."
        
        if f_mod == "Divide Curriculum into 3 Terms (Weekly Scheme)":
            prompt = f"Break down the {f_sub} curriculum for {f_cls} into 3 terms (1st, 2nd, 3rd), with 12 weeks each. {ref_context}"
        else:
            prompt = f"""Write a comprehensive Lesson Note for {f_cls}, {f_sub}.
            TERM: {f_trm} | WEEK: {f_wk} | TOPIC: {f_top}.
            {ref_context}
            
            FOLLOW THIS 18-POINT OUTLINE STRICTLY:
            1. Subject, 2. Date, 3. Class, 4. Duration, 5. Age, 6. Gender, 7. Theme, 
            8. Learning Outcome, 9. Focal Competence, 10. Topic, 11. Performance Objectives, 
            12. Teaching Resources, 13. Previous Knowledge, 14. Presentation (Steps), 
            15. Class Activities, 16. Evaluation, 17. Conclusion, 18. Assignment.
            Include a full student note at the end."""
            
        with st.spinner("Generating..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['out'] = chat.choices[0].message.content
            st.session_state['t'] = f"{f_cls}_{f_sub}"

# --- 5. RESULTS ---
if 'out' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['out'])
    
    f_data = create_docx(st.session_state['out'], st.session_state['t'])
    c_d, c_r = st.columns(2)
    c_d.download_button("📥 Download Word", f_data, f"{st.session_state['t']}.docx")
    if c_r.button("🗑️ Clear Results"):
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
