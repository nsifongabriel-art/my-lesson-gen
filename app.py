import streamlit as st
from groq import Groq
from docx import Document
from io import BytesIO
import re
import pandas as pd
from datetime import datetime

# --- 1. BRANDING & STYLE ---
st.set_page_config(page_title="VIKIDYL AI Pro", page_icon="🎓", layout="wide")

st.markdown("""
    <style>
    .stButton>button { width: 100%; border-radius: 25px; background-color: #1E88E5; color: white; height: 3.5em; font-weight: bold; }
    .footer { position: fixed; left: 0; bottom: 0; width: 100%; background-color: #f1f1f1; text-align: center; padding: 10px; font-size: 14px; border-top: 1px solid #e0e0e0; z-index: 99; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. LIVE SECURITY LAYER ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Q3UQhyOt8YS800kJ2aMw3bbsVpji-JUy_jU1shoeHYs/edit#gid=0"

def get_live_codes():
    try:
        base_url = SHEET_URL.split('/edit')[0]
        csv_url = f"{base_url}/export?format=csv"
        df = pd.read_csv(csv_url)
        df.columns = [c.strip().lower() for c in df.columns]
        return dict(zip(df['code'].astype(str), df['expiry'].astype(str)))
    except:
        return {"VIK-ADMIN-2026": "2027-01-01"}

def check_access(user_input):
    valid_codes = get_live_codes()
    if user_input in valid_codes:
        try:
            expiry_str = valid_codes[user_input].strip()
            expiry_date = datetime.strptime(expiry_str, "%Y-%m-%d")
            if datetime.now() <= expiry_date:
                return True, expiry_date.strftime("%d %B %Y")
            else:
                return False, "Expired"
        except:
            return False, "Date Format Error"
    return False, "Invalid Code"

if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    st.title("🔐 VIKIDYL AI - Secure Access")
    user_code = st.text_input("Enter Teacher Access Code", type="password")
    if st.button("Unlock System"):
        is_valid, status = check_access(user_code)
        if is_valid:
            st.session_state['authenticated'] = True
            st.session_state['expiry'] = status
            st.rerun()
        else:
            st.error(f"Access Denied: {status}")
    st.stop()

# --- 3. UTILITIES ---
def format_math_for_print(text):
    subs = {r'\\frac\{(.+?)\}\{(.+?)\}': r'(\1 / \2)', r'\\sqrt\{(.+?)\}': r'√(\1)', r'\\pm': '±', r'\\times': '×', r'\\div': '÷', r'\^2': '²', r'\^3': '³', r'\$': '', r'\\': ''}
    for pattern, replacement in subs.items():
        text = re.sub(pattern, replacement, text)
    return text

def create_docx(text, title):
    doc = Document(); doc.add_heading(f'VIKIDYL AI - {title}', 0)
    doc.add_paragraph(format_math_for_print(text))
    buffer = BytesIO(); doc.save(buffer); buffer.seek(0)
    return buffer

# --- 4. CURRICULUM DATA ---
CURRICULUM_DATA = {
    "Nursery": {"Classes": ["Pre-Nursery", "Nursery 1", "Nursery 2"], "Subjects": ["Letter Work", "Number Work", "Health Habits", "Social Norms", "Rhymes", "Science Experience"]},
    "Primary": {"Classes": ["Basic 1", "Basic 2", "Basic 3", "Basic 4", "Basic 5", "Basic 6"], "Subjects": ["Mathematics", "English Studies", "Basic Science & Tech", "Social Studies", "Nigerian History", "P.H.E", "Agriculture", "Home Economics"]},
    "Junior Secondary": {"Classes": ["JSS 1", "JSS 2", "JSS 3"], "Subjects": ["Mathematics", "English", "Basic Science", "Basic Technology", "Business Studies", "Civic Education", "Social Studies"]},
    "Senior Secondary": {"Classes": ["SSS 1", "SSS 2", "SSS 3"], "Subjects": ["Mathematics", "English Language", "Biology", "Chemistry", "Physics", "Further Maths", "Economics", "Government", "Food and Nutrition", "Financial Accounting"]}
}

# --- 5. MAIN APP ---
try:
    client = Groq(api_key=st.secrets["GROQ_API_KEY"])
except:
    st.error("🔑 API Key Error")
    st.stop()

st.sidebar.success("Access Active")
st.sidebar.write(f"Expires: {st.session_state['expiry']}")
if st.sidebar.button("Logout"):
    st.session_state['authenticated'] = False
    st.rerun()

st.title("🎓 VIKIDYL AI Professional")
tabs = st.tabs(["📝 Quick Tools", "📊 Assessment Builder", "📅 NERDC Scheme & Notes"])

# TAB 1: QUICK TOOLS
with tabs[0]:
    st.subheader("Fast Lesson Script")
    lvl_q = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_q")
    cls_q = st.selectbox("Class", CURRICULUM_DATA[lvl_q]["Classes"], key="cls_q")
    sub_q = st.selectbox("Subject", CURRICULUM_DATA[lvl_q]["Subjects"], key="sub_q")
    top_q = st.text_input("Topic", key="top_q")
    if st.button("Generate Script"):
        with st.spinner("Drafting..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Quick lesson script for {cls_q} {sub_q}: {top_q}"}])
            st.session_state['out'] = chat.choices[0].message.content

# TAB 2: ASSESSMENT
with tabs[1]:
    st.subheader("Assessment Builder")
    c1, c2 = st.columns(2)
    with c1:
        lvl_a = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_a")
        cls_a = st.selectbox("Class", CURRICULUM_DATA[lvl_a]["Classes"], key="cls_a")
        sub_a = st.selectbox("Subject", CURRICULUM_DATA[lvl_a]["Subjects"], key="sub_a")
    with c2:
        diff_a = st.selectbox("Tone", ["Standard", "Moderate", "Fun"], key="diff_a")
        top_a = st.text_area("Topics", key="top_a")
    if st.button("Generate Assessment"):
        with st.spinner("Creating questions..."):
            chat = client.chat.completions.create(model="llama-3.3-70b-versatile", messages=[{"role": "user", "content": f"Create {diff_a} exam for {cls_a} {sub_a} on: {top_a}"}])
            st.session_state['out'] = chat.choices[0].message.content

# TAB 3: NERDC (CHRONOLOGICAL LINKING)
with tabs[2]:
    st.subheader("NERDC Serialized Planner")
    col1, col2 = st.columns(2)
    with col1:
        lvl_f = st.selectbox("Level Group", list(CURRICULUM_DATA.keys()), key="lvl_f")
        cls_f = st.selectbox("Class", CURRICULUM_DATA[lvl_f]["Classes"], key="cls_f")
        sub_f = st.selectbox("Subject", CURRICULUM_DATA[lvl_f]["Subjects"], key="sub_f")
        trm_f = st.selectbox("Term", ["1st Term", "2nd Term", "3rd Term", "Full Year (All 3 Terms)"], key="trm_f")
    with col2:
        mode_f = st.radio("Action", ["Serialized Scheme (Week 1-12)", "Detailed Weekly Lesson Note"])
        manual_ref = st.text_area("Manual Reference (Optional Override)", height=70)
    
    wk_f, top_f = "N/A", "N/A"
    if mode_f == "Detailed Weekly Lesson Note":
        n1, n2 = st.columns(2)
        wk_f = n1.selectbox("Week", [f"Week {i}" for i in range(1, 13)])
        top_f = n2.text_input("Topic Name")

    if st.button("🚀 Generate NERDC Material"):
        if mode_f == "Serialized Scheme (Week 1-12)":
            if "Full Year" in trm_f:
                p = f"COMPLETE Serialized Scheme for {cls_f} {sub_f} ENTIRE YEAR. 3 terms, 12 weeks each (Total 36). Follow NERDC chronological progression. {manual_ref}"
            else:
                p = f"Serialized 12-week scheme for {cls_f} {sub_f} for {trm_f}. Ensure topics follow {trm_f} NERDC standards. {manual_ref}"
        else:
            # THIS IS THE KEY FIX: Linking the note to the term context
            p = f"""Write an 18-point Lesson Note for {cls_f} {sub_f}. 
            TERM: {trm_f} | WEEK: {wk_f} | TOPIC: {top_f}.
            CONTEXT: Since this is {trm_f}, ensure the content level and prior knowledge assumptions align with the NERDC Full Year progression. 
            Do NOT repeat 1st term foundations if this is 2nd or 3rd term. {manual_ref}"""
        
        with st.spinner("Processing..."):
            chat = client.chat.completions.create(
                model="llama-3.3-70b-versatile", 
                messages=[{"role": "system", "content": "Expert Nigerian NERDC consultant. You ensure that individual weekly notes align perfectly with the year-long curriculum map."},
                          {"role": "user", "content": p}]
            )
            st.session_state['out'] = chat.choices[0].message.content

# OUTPUT
if 'out' in st.session_state:
    st.markdown("---")
    st.markdown(st.session_state['out'])
    file = create_docx(st.session_state['out'], "Vikidyl_Output")
    st.download_button("📥 Download Word Doc", file, "Vikidyl_Material.docx")

st.markdown(f'<div class="footer"><p>Developed by <b>Ufford I.I. - Vikidyl Models Consult</b><br>Email: digitalisedmindset@gmail.com<br>© 2026 VIKIDYL AI</p></div>', unsafe_allow_html=True)
