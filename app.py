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
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & CONNECTION ---
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

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing! Please add GROQ_API_KEY to your Streamlit Secrets.")
    st.stop()

# --- 3. HELPER FUNCTIONS ---
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
st.caption("NERDC 2026 Curriculum Standard • Comprehensive Educator Suite")

tabs = st.tabs(["📝 Quick Lesson", "📊 Assessment Builder", "📅 Weekly Scheme & Full Notes"])

# --- TAB 1: QUICK TOOLS (RESTORED) ---
with tabs[0]:
    st.subheader("Fast 5-Step Lesson Script")
    col_a, col_b = st.columns(2)
    q_class = col_a.selectbox("Select Class", CLASSES, key="q_cls")
    q_tone = col_b.selectbox("Teaching Tone", ["Playful", "Formal", "Inquiry-based"], key="q_tone")
    
    q_sub = st.text_input("Subject/Topic", placeholder="e.g. Addition of Numbers", key="q_sub_input")
    
    if st.button("Generate Quick Script"):
        if q_sub:
            prompt = f"Create a quick 5-step lesson script for {q_class} on {q_sub}. Tone: {q_tone}. Include 'Teacher Says' and 'Write on Board'."
            with st.spinner("VIKIDYL AI is writing..."):
                chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state['output'] = chat.choices[0].message.content
                st.session_state['title'] = f"Quick Lesson: {q_sub}"

# --- TAB 2: ASSESSMENT (RESTORED) ---
with tabs[1]:
    st.subheader("Professional Test & Exam Generator")
    col_1, col_2 = st.columns(2)
    e_class = col_1.selectbox("Class Level", CLASSES, key="e_cls")
    e_type = col_2.selectbox("Assessment Type", ["Quiz", "Mid-Term Exam", "Full Term Exam"])
    
    e_sub = st.text_input("Subject", key="e_sub_input")
    e_topics = st.text_area("Topics to cover (separate with commas)")
    
    c1, c2 = st.columns(2)
    objs = c1.number_input("Number of MCQs", 5, 50, 10)
    theory = c2.number_input("Number of Theory Questions", 0, 10, 3)

    if st.button("Generate Assessment"):
        prompt = f"Create a {e_type} for {e_class} {e_sub}. Include {objs} Multiple Choice Questions and {theory} Theory questions. Based on: {e_topics}. Provide an Answer Key."
        with st.spinner("Setting questions..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
            st.session_state['output'] = chat.choices[0].message.content
            st.session_state['title'] = f"{e_type}: {e_sub}"

# --- TAB 3: WEEKLY SCHEME & NOTES ---
with tabs[2]:
    st.subheader("Detailed Weekly Planner (NERDC Format)")
    col_in, col_out = st.columns([1, 2])
    
    with col_in:
        sel_class = st.selectbox("Specific Class", CLASSES, key="f_cls")
        if "Nursery" in sel_class or "Pre" in sel_class:
            subs = SUBJECT_LISTS["Nursery"]
        elif "Primary" in sel_class:
            subs = SUBJECT_LISTS["Primary"]
        else:
            subs = SUBJECT_LISTS["Secondary"]
            
        sel_sub = st.selectbox("Subject", subs, key="f_sub")
        term = st.selectbox("Term", ["1st Term", "2nd Term", "3rd Term"], key="f_term")
        mode = st.radio("Action", ["Generate 12-Week Scheme", "Generate Weekly Note of Lesson"], key="f_mode")
        
        if mode == "Generate Weekly Note of Lesson":
            week = st.number_input("Week", 1, 12, 1, key="f_wk")
            topic = st.text_input("Weekly Topic", key="f_top")
        
        if st.button("Generate Professional Plan"):
            if mode == "Generate 12-Week Scheme":
                prompt = f"Create a 12-week NERDC Scheme of Work for {sel_class}, {sel_sub} for {term}."
            else:
                prompt = f"Write a full NERDC Lesson Note for {sel_class}, {sel_sub}, Week {week}, Topic: {topic}. Include Objectives, Instructional Materials, Step-by-Step Presentation, and Student Note."
            
            with st.spinner("Generating..."):
                chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": prompt}])
                st.session_state['output'] = chat.choices[0].message.content
                st.session_state['title'] = f"{sel_class} {sel_sub} Plan"

# --- 5. GLOBAL OUTPUT & DOWNLOAD ---
if 'output' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['output'])
    
    file_data = create_docx(st.session_state['output'], st.session_state.get('title', 'Material'))
    st.download_button(
        label="📥 Download Word Document",
        data=file_data,
        file_name="VIKIDYL_AI_Output.docx",
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )

# --- 6. FOOTER ---
# Update "yourname@email.com" to your actual email!
st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="footer">
        <p>Developed by <b>Ufford I.I.</b> | Support: <a href="mailto:yourname@email.com">digitalisedmindset@gmail.com</a><br>
        © 2026 VIKIDYL AI - Empowering Educators Worldwide</p>
    </div>
    """, unsafe_allow_html=True)
