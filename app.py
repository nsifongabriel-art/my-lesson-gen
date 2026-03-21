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
    @media print { .no-print { display: none !important; } .print-only { display: block !important; } }
    </style>
    """, unsafe_allow_html=True)

# --- 2. CLASS-SPECIFIC DATA ---
CLASSES = [
    "Pre-Nursery", "Nursery 1", "Nursery 2", 
    "Primary 1", "Primary 2", "Primary 3", "Primary 4", "Primary 5", "Primary 6",
    "JSS 1", "JSS 2", "JSS 3", 
    "SSS 1", "SSS 2", "SSS 3"
]

SUBJECT_LISTS = {
    "Nursery": ["Numeracy", "Literacy", "Health Habits", "Social Norms", "Rhymes"],
    "Primary": ["Mathematics", "English Studies", "Basic Science", "Social Studies", "Nigerian History", "P.H.E", "Agriculture"],
    "Secondary": ["Mathematics", "English", "Biology", "Physics", "Chemistry", "Economics", "Civic Education", "Further Maths"]
}

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing! Please check your Streamlit Secrets.")
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
st.caption("NERDC Curriculum Compliant • Class-Specific Intelligence")

tabs = st.tabs(["📝 Quick Tools", "📊 Assessment", "📅 Weekly Scheme & Full Notes"])

# --- TAB 3: CLASS-BASED SCHEME & NOTES ---
with tabs[2]:
    st.subheader("Comprehensive Weekly Planner")
    
    col_input, col_output = st.columns([1, 2])
    
    with col_input:
        selected_class = st.selectbox("Select Specific Class", CLASSES)
        
        # Determine which subject list to show based on class name
        if "Nursery" in selected_class or "Pre" in selected_class:
            subs = SUBJECT_LISTS["Nursery"]
        elif "Primary" in selected_class:
            subs = SUBJECT_LISTS["Primary"]
        else:
            subs = SUBJECT_LISTS["Secondary"]
            
        selected_subject = st.selectbox("Subject", subs)
        term = st.selectbox("Term", ["1st Term", "2nd Term", "3rd Term"])
        mode = st.radio("Choose Action", ["Generate 12-Week Scheme", "Generate Weekly Note of Lesson"])
        
        if mode == "Generate Weekly Note of Lesson":
            week = st.number_input("Week Number", 1, 12, 1)
            topic = st.text_input("Topic for Week " + str(week))
        
        generate_btn = st.button("Generate for " + selected_class)

    with col_output:
        if generate_btn:
            if mode == "Generate 12-Week Scheme":
                prompt = f"Create a 12-week Scheme of Work for {selected_class}, {selected_subject} for {term}. Use Nigerian NERDC format. Group by Week 1 to 12 with Topic and Learning Objectives for each."
            else:
                prompt = f"""Write a detailed Lesson Note for {selected_class}. 
                Subject: {selected_subject} | Week: {week} | Topic: {topic}.
                Follow this NERDC structure:
                - BEHAVIORAL OBJECTIVES
                - INSTRUCTIONAL MATERIALS
                - STEP-BY-STEP PRESENTATION (Teacher/Pupil Activities)
                - EVALUATION
                - COMPREHENSIVE NOTE FOR PUPILS (To be copied into notebooks)
                """
            
            with st.spinner("VIKIDYL AI is processing..."):
                chat = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": f"You are a professional teacher specializing in {selected_class}."},
                              {"role": "user", "content": prompt}]
                )
                st.session_state['full_note'] = chat.choices[0].message.content
                st.session_state['note_title'] = f"{selected_class} {selected_subject} Week {week if mode != 'Generate 12-Week Scheme' else 'Scheme'}"

        if 'full_note' in st.session_state:
            st.markdown("---")
            st.info("💡 To Print: Right-click and choose 'Print' or use the Download button below.")
            st.markdown(st.session_state['full_note'])
            
            # Download Button
            file_data = create_docx(st.session_state['full_note'], st.session_state['note_title'])
            st.download_button(
                label="📥 Download Word Document",
                data=file_data,
                file_name=f"{st.session_state['note_title']}.docx",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )

# --- FOOTER ---
# Update "your@email.com" with your actual email!
st.markdown(f"""
    <div style="height: 100px;"></div>
    <div class="footer">
        <p>Developed by <b>Ufford I.I.</b> | Support: <a href="mailto:your@email.com">digitalisedmindset@gmail.com</a><br>
        © 2026 VIKIDYL AI - Empowering Excellence in Education</p>
    </div>
    """, unsafe_allow_html=True)
