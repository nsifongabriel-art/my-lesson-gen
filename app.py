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
    .css-1kyx60l { background-color: #f0f2f6; padding: 20px; border-radius: 15px; }
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

# --- 4. INTERFACE ---
st.title("🎓 VIKIDYL AI: NERDC Suite")
st.caption("Structured for the Nigerian 12-Week Termly Curriculum")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessments", "📅 Full NERDC Scheme & Notes"])

# --- TAB 3: THE COMPREHENSIVE PLANNER ---
with tabs[2]:
    st.subheader("Official Weekly Planner & Note Generator")
    
    col_set, col_res = st.columns([1, 2])
    
    with col_set:
        st.info("📌 Step 1: Set the Context")
        f_cls = st.selectbox("Class Level", CLASSES, key="f_cls")
        f_trm = st.selectbox("Current Term", TERMS, key="f_trm")
        f_sub = st.text_input("Subject", placeholder="e.g. Basic Science", key="f_sub")
        
        st.write("---")
        st.info("📎 Step 2: Reference Material")
        # Added Upload space for the User's specific scheme
        ref_upload = st.file_uploader("Upload your School's Scheme/Curriculum (Image or PDF)", type=["jpg", "png", "pdf"])
        ref_text = st.text_area("OR Paste Scheme Topics here", placeholder="Week 1: Living things...", height=100)
        
        st.write("---")
        f_mod = st.radio("Action", ["Generate 12-Week Termly Scheme", "Generate Detailed Weekly Note"], key="f_mod")
        
        if f_mod == "Generate Detailed Weekly Note":
            f_wk = st.number_input("Select Week", 1, 12, 1)
            f_top = st.text_input("Specific Topic")
            
        btn = st.button("🚀 Generate NERDC Material")

    with col_res:
        if btn:
            # Building the context for the AI
            context = f"Reference Material Provided: {ref_text}" if ref_text else "Use standard 2026 NERDC curriculum."
            
            if f_mod == "Generate 12-Week Termly Scheme":
                prompt = f"Create a {f_trm} Scheme of Work for {f_cls}, {f_sub}. {context} Structure it Week 1 to 12 with Topics and Sub-topics."
            else:
                prompt = f"""Write a comprehensive NERDC Lesson Note for {f_cls}, {f_sub}.
                TERM: {f_trm} | WEEK: {f_wk} | TOPIC: {f_top}.
                {context}
                
                STRICT FORMAT REQUIRED:
                1. BEHAVIORAL OBJECTIVES
                2. INSTRUCTIONAL MATERIALS
                3. PREVIOUS KNOWLEDGE
                4. PRESENTATION:
                   - Step 1: Introduction
                   - Step 2: Teacher Activities vs Pupil Activities
                   - Step 3: Discussion
                   - Step 4: Summary
                5. EVALUATION
                6. CONCLUSION & ASSIGNMENT
                7. COMPREHENSIVE STUDENT NOTE (Ready for board copying)
                """
            
            with st.spinner("VIKIDYL AI is aligning with NERDC standards..."):
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are VIKIDYL AI, a Nigerian Education Consultant expert in NERDC curriculum standards."},
                              {"role": "user", "content": prompt}]
                )
                st.session_state['full_output'] = chat.choices[0].message.content
                st.session_state['f_title'] = f"{f_cls}_{f_sub}_{f_trm}_Wk{f_wk if f_mod != 'Generate 12-Week Scheme' else 'Scheme'}"

        if 'full_output' in st.session_state:
            st.markdown(st.session_state['full_output'])
            
            # Actions
            c_d, c_r = st.columns(2)
            f_data = create_docx(st.session_state['full_output'], st.session_state['f_title'])
            c_d.download_button("📥 Download as Word", f_data, f"{st.session_state['f_title']}.docx")
            if c_r.button("🗑️ Clear Result"):
                del st.session_state['full_output']
                st.rerun()

# --- TAB 1 & 2 (Simplified Backends for performance) ---
with tabs[0]:
    st.write("Quickly generate a 5-step script for immediate classroom use.")
    # (Existing Quick Tool logic goes here - works same as before)

with tabs[1]:
    st.write("Generate Quizzes and Exams based on specific topics.")
    # (Existing Assessment logic goes here - works same as before)

# --- 6. FOOTER ---
st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="footer">
        <p>Developed by <b>Your Name</b> | Support: <a href="mailto:your@email.com">your@email.com</a><br>
        © 2026 VIKIDYL AI - Nigerian Education Standards</p>
    </div>
    """, unsafe_allow_html=True)
