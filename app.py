import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

def create_docx(text):
    doc = Document()
    doc.add_heading('Academic Material', 0)
    doc.add_paragraph(text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Edu-Planner Pro", layout="wide")
st.title("🍎 Advanced Edu-Planner")

# Sidebar Configuration
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
mode = st.sidebar.selectbox("Select Mode", ["Detailed Lesson Note", "Custom Assessment"])

# Persistent storage
if 'generated_content' not in st.session_state:
    st.session_state['generated_content'] = ""

# --- MODE 1: DETAILED LESSON NOTE ---
if mode == "Detailed Lesson Note":
    st.subheader("📚 5-Step Lesson Generator")
    topic = st.text_input("Topic")
    grade = st.text_input("Grade Level")
    
    if st.button("Generate Full Lesson"):
        if not api_key: st.error("Enter API Key")
        else:
            client = Groq(api_key=api_key)
            system_msg = """You are an expert Educator. Create a lesson using the 5-Step Approach:
            1. Anticipatory Set (Hook)
            2. Instruction (Detailed definitions and core concepts)
            3. Guided Practice (Worked examples)
            4. Independent Practice (Classwork)
            5. Closure (Summary & Homework).
            IMPORTANT: Include a separate section titled 'STUDENT NOTE' which is a simplified, copy-friendly version for students' notebooks."""
            
            with st.spinner("Writing detailed notes..."):
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_msg},
                              {"role": "user", "content": f"Topic: {topic}, Grade: {grade}"}]
                )
                st.session_state['generated_content'] = completion.choices[0].message.content

# --- MODE 2: CUSTOM ASSESSMENT ---
else:
    st.subheader("📝 Examination & Test Builder")
    col1, col2 = st.columns(2)
    with col1:
        weeks = st.text_input("Period (e.g., Week 1-3)")
        num_obj = st.number_input("Number of Objectives (MCQs)", min_value=0, value=10)
    with col2:
        num_theory = st.number_input("Number of Theory/Subjective", min_value=0, value=3)
        scheme = st.text_area("Paste relevant Scheme of Work for these weeks")

    if st.button("Generate Examination"):
        if not api_key: st.error("Enter API Key")
        else:
            client = Groq(api_key=api_key)
            prompt = f"""Create a test for {weeks}. 
            Requirements:
            - {num_obj} Multiple Choice Questions (Objectives)
            - {num_theory} Theory/Subjective questions.
            - Include an Answer Key at the end.
            Base it on this scheme: {scheme}"""
            
            with st.spinner("Setting questions..."):
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are an Examination Officer."},
                              {"role": "user", "content": prompt}]
                )
                st.session_state['generated_content'] = completion.choices[0].message.content

# --- DOWNLOAD AREA ---
if st.session_state['generated_content']:
    st.markdown("---")
    st.markdown(st.session_state['generated_content'])
    file = create_docx(st.session_state['generated_content'])
    st.download_button("📥 Download Word Doc", file, "EduMaterial.docx")
