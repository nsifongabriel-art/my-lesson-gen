import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="VIKIDYL AI Pro", page_icon="🎓", layout="wide")

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
        background-color: #f1f1f1; text-align: center; 
        padding: 10px; font-size: 14px; border-top: 1px solid #e0e0e0; z-index: 99; 
    }
    .stTabs [data-baseweb="tab-list"] { gap: 10px; }
    .stTabs [data-baseweb="tab"] { 
        background-color: #e3f2fd; border-radius: 10px 10px 0 0; padding: 10px; 
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA ---
CLASSES = [
    "Pre-Nursery", "Nursery 1", "Nursery 2", 
    "Primary 1", "Primary 2", "Primary 3", "Primary 4", "Primary 5", "Primary 6",
    "JSS 1", "JSS 2", "JSS 3", "SSS 1", "SSS 2", "SSS 3"
]

SUBJECT_LISTS = {
    "Nursery": ["Numeracy", "Literacy", "Health Habits", "Social Norms", "Rhymes", "Creative Arts"],
    "Primary": ["Mathematics", "English Studies", "Basic Science", "Social Studies", "Nigerian History", "P.H.E", "Agriculture", "Home Economics"],
    "Secondary": ["Mathematics", "English", "Biology", "Physics", "Chemistry", "Economics", "Civic Education", "Further Maths", "Government", "Literature"]
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

# --- 4. INTERFACE ---
st.title("🎓 VIKIDYL AI Professional")
st.caption("Official 2026 NERDC Curriculum Standards")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessment Builder", "📅 Weekly Scheme & Full Notes"])

# --- TAB 1: QUICK TOOLS ---
with tabs[0]:
    st.subheader("Fast 5-Step Lesson Script")
    c1, c2 = st.columns(2)
    q_cls = c1.selectbox("Class", CLASSES, key="q_cls")
    q_ton = c2.selectbox("Tone", ["Playful", "Formal", "Inquiry-based"], key="q_ton")
    q_sub = st.text_input("Topic", placeholder="e.g. Parts of a Plant", key="q_in")
    
    if st.button("Generate Script"):
        if q_sub:
            with st.spinner("VIKIDYL AI is drafting..."):
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "user", "content": f"Create a 5-step script for {q_cls} on {q_sub}. Tone: {q_ton}. Use 'Teacher Says' and 'Write on Board'."}]
                )
                st.session_state['output'] = chat.choices[0].message.content
                st.session_state['title'] = f"Quick Script: {q_sub}"

# --- TAB 2: ASSESSMENT ---
with tabs[1]:
    st.subheader("Test & Exam Generator")
    c3, c4 = st.columns(2)
    e_cls = c3.selectbox("Class", CLASSES, key="e_cls")
    e_typ = c4.selectbox("Type", ["Quiz", "Mid-Term", "Exam"], key="e_typ")
    e_sub = st.text_input("Subject", key="e_sub")
    e_top = st.text_area("Topics (comma separated)", key="e_top")
    
    if st.button("Generate Assessment"):
        with st.spinner("Setting questions..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": f"Create {e_typ} for {e_cls} {e_sub} on {e_top}. Include 10 MCQs, 3 Theory, and Answer Key."}]
            )
            st.session_state['output'] = chat.choices[0].message.content
            st.session_state['title'] = f"{e_typ}: {e_sub}"

# --- TAB 3: WEEKLY SCHEME & NOTES ---
with tabs[2]:
    st.subheader("NERDC Full Lesson Planner")
    col_in, col_out = st.columns([1, 2])
    
    with col_in:
        f_cls = st.selectbox("Specific Class", CLASSES, key="f_cls")
        group = "Nursery" if "Nursery" in f_cls else "Primary" if "Primary" in f_cls else "Secondary"
        f_sub = st.selectbox("Subject", SUBJECT_LISTS[group], key="f_sub")
        f_mod = st.radio("Action", ["12-Week Scheme", "Full Lesson Note"], key="f_mod")
        
        if f_mod == "Full Lesson Note":
            f_wk = st.number_input("Week", 1, 12, 1)
            f_top = st.text_input("Topic")
            
        if st.button("Generate Professional Plan"):
            prompt = f"NERDC Format: {'Scheme of Work' if f_mod == '12-Week Scheme' else 'Lesson Note'} for {f_cls} {f_sub}. {'Week '+str(f_wk)+' Topic: '+f_top if f_mod != '12-Week Scheme' else ''}. Include Teacher and Pupil Activities."
            with st.spinner("Generating..."):
                chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state['output'] = chat.choices[0].message.content
                st.session_state['title'] = f"{f_cls} {f_sub}"

# --- 5. RESULTS & ACTIONS ---
if 'output' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['output'])
    
    c_d, c_c = st.columns(2)
    
    file = create_docx(st.session_state['output'], st.session_state['title'])
    c_d.download_button("📥 Download Word Doc", file, f"{st.session_state['title']}.docx")
    
    if c_c.button("🗑️ Clear Results"):
        del st.session_state['output']
        st.rerun()

# --- 6. FOOTER ---
st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="footer">
        <p>Developed by <b>Ufford I.I.</b> | Support: <a href="mailto:yourname@email.com">digitalisedmindset@gmail.com</a><br>
        © 2026 VIKIDYL AI - Nigerian Education Standard</p>
    </div>
    """, unsafe_allow_html=True)
