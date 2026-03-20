import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO

def create_docx(text):
    doc = Document()
    doc.add_heading('Ready-to-Use Academic Material', 0)
    # Cleaning LaTeX symbols for Word export
    clean_text = text.replace('$', '') 
    doc.add_paragraph(clean_text)
    buffer = BytesIO()
    doc.save(buffer)
    buffer.seek(0)
    return buffer

st.set_page_config(page_title="Edu-Planner Pro", layout="wide")
st.title("🍎 Professional Edu-Planner")

api_key = st.sidebar.text_input("Enter Groq API Key", type="password")
mode = st.sidebar.selectbox("Select Mode", ["Detailed Lesson Note", "Custom Assessment"])

if 'generated_content' not in st.session_state:
    st.session_state['generated_content'] = ""

if mode == "Detailed Lesson Note":
    st.subheader("📚 Scripted 5-Step Lesson Note")
    topic = st.text_input("Topic (e.g., Quadratic Equations)")
    grade = st.text_input("Grade Level")
    
    if st.button("Generate Ready-to-Use Lesson"):
        if not api_key: st.error("Enter API Key")
        else:
            client = Groq(api_key=api_key)
            # THE KEY CHANGE: Explicit instructions for Math and Scripting
            system_msg = """You are a Master Teacher. 
            1. MATH FORMATTING: Use LaTeX for all mathematical symbols and formulas (e.g., use $x^2$ or $\\frac{a}{b}$). 
            2. TEACHER SCRIPT: Write exactly what the teacher should say. Use 'Teacher Says:' and 'Write on Board:'.
            3. CONTENT: Follow the 5-step approach.
            4. STUDENT NOTE: Provide a clear, structured note for students to copy word-for-word. 
            Do not give advice; give the actual content."""
            
            with st.spinner("Preparing your script..."):
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": system_msg},
                              {"role": "user", "content": f"Topic: {topic}, Grade: {grade}"}]
                )
                st.session_state['generated_content'] = completion.choices[0].message.content

else:
    st.subheader("📝 Examination & Test Builder")
    col1, col2 = st.columns(2)
    with col1:
        weeks = st.text_input("Period (e.g., Week 1-3)")
        num_obj = st.number_input("Number of Objectives", min_value=0, value=10)
    with col2:
        num_theory = st.number_input("Number of Theory", min_value=0, value=3)
        scheme = st.text_area("Paste Scheme of Work")

    if st.button("Generate Examination"):
        if not api_key: st.error("Enter API Key")
        else:
            client = Groq(api_key=api_key)
            prompt = f"""Create a test for {weeks}. Use LaTeX for all math.
            - {num_obj} Objectives
            - {num_theory} Theory questions.
            - Provide a clear Answer Key.
            Base it on: {scheme}"""
            
            with st.spinner("Setting exam..."):
                completion = client.chat.completions.create(
                    model="llama-3.3-70b-versatile",
                    messages=[{"role": "system", "content": "You are an Examination Officer. Use LaTeX for math symbols."},
                              {"role": "user", "content": prompt}]
                )
                st.session_state['generated_content'] = completion.choices[0].message.content

if st.session_state['generated_content']:
    st.markdown("---")
    # This line tells Streamlit to render the Math symbols correctly
    st.markdown(st.session_state['generated_content'])
    
    file = create_docx(st.session_state['generated_content'])
    st.download_button("📥 Download Word Doc", file, "Lesson_Material.docx")
