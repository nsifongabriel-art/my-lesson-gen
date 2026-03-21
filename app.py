import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO
from PIL import Image

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="VIKIDYL AI Pro", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #1E88E5; color: white; height: 3.5em; font-weight: bold; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f1f1; text-align: center; padding: 10px; font-size: 14px; border-top: 1px solid #e0e0e0; z-index: 99; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. DATA & CONNECTION ---
LEVELS = {
    "Pre-Nursery/Nursery": ["Letter Work", "Number Work", "Science Experience", "Social Norms"],
    "Primary (Basic 1-6)": ["Mathematics", "English Studies", "Basic Science", "Nigerian History", "Digital Literacy"],
    "Junior College (JSS 1-3)": ["Mathematics", "English", "Basic Tech", "Business Studies", "Nigerian History"],
    "Senior College (SSS 1-3)": ["Mathematics", "English", "Biology", "Physics", "Chemistry", "Economics", "Citizenship Studies"]
}

try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except Exception:
    st.error("🔑 API Key Missing!")
    st.stop()

# --- 3. THE INTERFACE ---
st.title("🎓 VIKIDYL AI: Professional Suite")

tabs = st.tabs(["📚 Quick Lesson", "📊 Exams", "📅 Full Weekly Note & Scheme"])

# --- TAB 3: THE NEW COMPREHENSIVE SECTION ---
with tabs[2]:
    st.subheader("Weekly Note of Lesson & Scheme Generator")
    st.info("Upload your curriculum screenshot or type the topic to generate a full 12-week scheme and detailed notes.")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        level = st.selectbox("School Level", list(LEVELS.keys()), key="full_lvl")
        subj = st.selectbox("Subject", LEVELS[level], key="full_sub")
        term = st.selectbox("Term", ["First Term", "Second Term", "Third Term"])
        
        # Screenshot Upload Feature
        uploaded_file = st.file_uploader("Upload Curriculum Screenshot (Optional)", type=["jpg", "png", "jpeg"])
        if uploaded_file:
            st.image(uploaded_file, caption="Curriculum Loaded", width=200)

    with col2:
        action = st.radio("What do you want to generate?", ["12-Week Termly Scheme", "Full Comprehensive Lesson Note (Weekly)"])
        
        if action == "12-Week Termly Scheme":
            if st.button("Generate Termly Plan"):
                prompt = f"Create a 12-week Scheme of Work for {subj} at {level} level for {term} using the Nigerian NERDC 2026 curriculum. List Week 1 to 12 topics."
                with st.spinner("Organizing your term..."):
                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": prompt}]
                    )
                    st.session_state['full_out'] = chat.choices[0].message.content

        else:
            week_no = st.number_input("Week Number", 1, 12, 1)
            topic = st.text_input("Topic for this Week")
            
            if st.button("Generate Comprehensive Note"):
                # System instructions to follow the NERDC format strictly
                nerdc_prompt = f"""
                Write a professional Nigerian Lesson Note for Week {week_no}.
                Level: {level} | Subject: {subj} | Topic: {topic}.
                
                Follow this NERDC format:
                1. TOPIC & SUB-TOPIC
                2. FOCAL COMPETENCE (Skills the students will gain)
                3. LEARNING OUTCOMES (Behavioral Objectives)
                4. PREVIOUS KNOWLEDGE
                5. INSTRUCTIONAL MATERIALS
                6. PRESENTATION (Step 1 to Step 4: Teacher & Pupil activities)
                7. EVALUATION / SUMMARY
                8. COMPREHENSIVE STUDENT NOTE (Ready for the board)
                """
                with st.spinner("Writing comprehensive note..."):
                    chat = client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": "user", "content": nerdc_prompt}]
                    )
                    st.session_state['full_out'] = chat.choices[0].message.content

    if 'full_out' in st.session_state:
        st.markdown("---")
        st.markdown(st.session_state['full_out'])

# --- FOOTER ---
st.markdown(f"""
    <div class="footer">
        <p>Developed by <b>Ufford I  I</b> |Contact:<ahref=">mailto:your@email.com">digitalisedmindset@gmail.com</a><br>©VIKIDYL AI - NERDC Standard 2026</p>
    </div>
    """, unsafe_allow_html=True)
