import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

# --- BRANDING & STYLING ---
st.set_page_config(page_title="Chalkie Clone Pro", page_icon="🎓", layout="centered")

# Custom CSS to make it look "Premium"
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stButton>button { width: 100%; border-radius: 20px; background-color: #4A90E2; color: white; }
    .stTextInput>div>div>input { border-radius: 10px; }
    </style>
    """, unsafe_allow_html=True)

# Function to create the Word Doc
def create_docx(text):
    doc = Document()
    doc.add_heading('Academic Material', 0)
    clean_text = text.replace('$', '') 
    doc.add_paragraph(clean_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

# --- LOGO AND TITLE ---
st.image("https://cdn-icons-png.flaticon.com/512/3426/3426653.png", width=80) # Replace with your logo URL
st.title("Chalkie AI: Master Planner")
st.caption("Empowering Teachers with AI-Driven Curriculum Design")

# --- SECURITY: LOAD API KEY FROM SECRETS ---
# This looks for the key you saved in the Streamlit Settings
try:
    api_key = st.secrets["GROQ_API_KEY"]
except:
    st.error("API Key not found in Secrets! Please add it to your Streamlit settings.")
    st.stop()

client = Groq(api_key=api_key)

# --- APP LOGIC ---
mode = st.tabs(["📚 Lesson Notes", "📝 Exams & Tests"])

with mode[0]:
    st.subheader("5-Step Scripted Lesson")
    topic = st.text_input("Enter Topic", placeholder="e.g. Simultaneous Equations")
    grade = st.text_input("Grade Level", placeholder="e.g. JSS3")
    
    if st.button("Generate Pro Lesson Plan"):
        system_msg = """You are a Master Teacher. 
        Format: Use LaTeX for ALL math ($...$). 
        Style: Write as a DIRECT SCRIPT. Use 'Teacher Says:' and 'Write on Board:'.
        Sections: 1. Hook, 2. Instruction, 3. Guided Examples, 4. Classwork, 5. Student Copyable Note."""
        
        with st.spinner("Writing your professional script..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": system_msg},
                          {"role": "user", "content": f"Topic: {topic}, Grade: {grade}"}]
            )
            st.session_state['output'] = completion.choices[0].message.content

with mode[1]:
    st.subheader("Exam Builder")
    weeks = st.text_input("Coverage", placeholder="e.g. Weeks 1-6")
    c1, c2 = st.columns(2)
    obj_count = c1.number_input("Objectives", 5, 50, 10)
    theory_count = c2.number_input("Theory", 1, 10, 3)
    scheme = st.text_area("Paste Scheme of Work")

    if st.button("Generate Examination Paper"):
        with st.spinner("Drafting exam..."):
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "system", "content": "You are an Examination Officer. Use LaTeX for math."},
                          {"role": "user", "content": f"Create {obj_count} OBJs and {theory_count} Theory questions for {weeks} based on: {scheme}"}]
            )
            st.session_state['output'] = completion.choices[0].message.content

# --- OUTPUT AND DOWNLOAD ---
if 'output' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['output'])
    file = create_docx(st.session_state['output'])
    st.download_button("📥 Download Official Document", file, "Academic_Material.docx")
