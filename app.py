import streamlit as st
from groq import Groq

# 1. Page Setup
st.set_page_config(page_title="AI Lesson Architect", page_icon="📚")
st.title("📚 AI Lesson Architect")
st.write("Generate full lesson plans with examples and homework.")

# 2. Sidebar for API Key (Keep it secure!)
api_key = st.sidebar.text_input("Enter Groq API Key", type="password")

# 3. User Inputs
topic = st.text_input("What is the lesson topic?")
grade = st.selectbox("Select Grade Level", ["Primary", "Secondary", "University"])

if st.button("Generate Lesson Plan"):
    if not api_key:
        st.error("Please enter your API Key in the sidebar!")
    else:
        client = Groq(api_key=api_key)
        
        with st.spinner("Writing your detailed lesson..."):
            system_instruction = """
            You are a Master Teacher. Create a HIGHLY DETAILED lesson plan.
            Include: 1. Objectives, 2. Direct Instruction, 3. Three Worked Examples, 
            4. Five Classwork Questions, 5. Three Homework Questions.
            """
            
            completion = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": f"Create a lesson on {topic} for {grade}."}
                ]
            )
            
            st.markdown("---")
            st.markdown(completion.choices[0].message.content)
