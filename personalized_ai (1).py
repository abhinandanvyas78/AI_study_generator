import streamlit as st
import google.generativeai as genai
import re
import os
import pyttsx3
import threading
from fpdf import FPDF
# Configure Google Gemini API
genai.configure(api_key=ENTER_YOUR_API_KEY)

tts_engine = pyttsx3.init()
audio_playing = False

def speak_text(text):
    """Speak the generated study material using TTS in a separate thread."""
    global audio_playing
    if audio_playing:
        return  # Prevent multiple audio playbacks
    audio_playing = True

    def run_tts():
        global audio_playing
        tts_engine.say(text)
        tts_engine.runAndWait()
        audio_playing = False  # Reset flag after completion

    threading.Thread(target=run_tts, daemon=True).start()
def stop_audio():
    """Stop audio playback immediately."""
    global tts_engine, audio_playing
    if audio_playing:
        tts_engine.stop()  # Stop TTS
        audio_playing = False

# TTS Functionality
def speak_text(text):
    global audio_thread, stop_audio_flag

    # Stop any ongoing audio before starting a new one
    stop_audio()

    def run_tts():
        global stop_audio_flag
        stop_audio_flag = False
        tts_engine.say(text)
        tts_engine.runAndWait()

    audio_thread = threading.Thread(target=run_tts)
    audio_thread.start()


def stop_audio():
    global stop_audio_flag
    stop_audio_flag = True
    tts_engine.stop()
        
# Function to clean generated content
def clean_text(text):
    text = re.sub(r"[*#]", "", text)  # Remove *, # symbols
    text = re.sub(r"\n\s*\n", "\n\n", text)  # Remove excessive newlines
    return text.strip()

# Function to sanitize filenames
def sanitize_filename(name):
    """Removes invalid characters from filenames."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

# Directories for storing data
DATA_DIRS = {
    "syllabus": "syllabus_data",
    "lesson_plan": "lesson_plans",
    "study_material": "study_material"
}
DATA_DIRS["quizzes"] = "quizzes"
os.makedirs(DATA_DIRS["quizzes"], exist_ok=True)
for path in DATA_DIRS.values():
    os.makedirs(path, exist_ok=True)

# Save and Load Data
def save_data(directory, filename, content):
    with open(os.path.join(directory, filename), "w", encoding="utf-8") as file:
        file.write(content)

def load_data(directory, filename):
    file_path = os.path.join(directory, filename)
    return open(file_path, "r", encoding="utf-8").read() if os.path.exists(file_path) else None

# Generate syllabus
def generate_syllabus(subject):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(f"Generate a structured syllabus for {subject}, listing topics only.")
        syllabus_text = clean_text(response.text) if hasattr(response, 'text') else "Error: No response from API"
        save_data(DATA_DIRS['syllabus'], f"syllabus_{sanitize_filename(subject)}.txt", syllabus_text)
        return syllabus_text
    except Exception as e:
        return f"Error generating syllabus: {e}"

# Generate lesson plan (Day-wise)
def generate_lesson_plan(subject, duration):
    syllabus_text = load_data(DATA_DIRS['syllabus'], f"syllabus_{sanitize_filename(subject)}.txt")
    if not syllabus_text:
        return "No syllabus found."
    topics = [t.strip() for t in syllabus_text.split("\n") if t.strip()]
    if not topics:
        return "No topics found in the syllabus."
    
    lessons_per_day = max(1, len(topics) // duration)
    plan = {f"Day {i+1}": topics[i * lessons_per_day:(i + 1) * lessons_per_day] for i in range(duration)}

    # Save the lesson plan
    lesson_plan_text = "\n".join([f"{day}: {', '.join(topics)}" for day, topics in plan.items()])
    save_data(DATA_DIRS['lesson_plan'], f"lesson_plan_{sanitize_filename(subject)}_{duration}days.txt", lesson_plan_text)
    
    return plan
def get_topic_result(topic):
    """Fetches key details about a given topic."""
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        prompt = (
            f"Provide a concise and well-structured summary of the topic '{topic}'. "
            "Include: Definition, Importance, Key Points, and a Practical Example."
        )
        response = model.generate_content(prompt)
        return clean_text(response.text) if hasattr(response, 'text') else "Error: No response from API"
    except Exception as e:
        return f"Error fetching result: {e}"
# Generate study material (Day-wise)
def generate_study_material(subject, day, topics):
    study_content = {}
    for topic in topics:
        safe_topic = sanitize_filename(topic)  # Clean topic name
        material_path = os.path.join(DATA_DIRS['study_material'], f"study_{sanitize_filename(subject)}_{safe_topic}.txt")

        if os.path.exists(material_path):
            study_content[topic] = load_data(DATA_DIRS['study_material'], f"study_{sanitize_filename(subject)}_{safe_topic}.txt")
        else:
            try:
                model = genai.GenerativeModel("gemini-1.5-flash")
                prompt = (
                    f"Provide a well-structured, detailed explanation of the topic '{topic}' in '{subject}'. "
                    "Include: Definition, Importance, Key Concepts, Examples, and Applications."
                )
                response = model.generate_content(prompt)
                material = clean_text(response.text) if hasattr(response, 'text') else "Error: No study material generated."
                save_data(DATA_DIRS['study_material'], f"study_{sanitize_filename(subject)}_{safe_topic}.txt", material)
                study_content[topic] = material
            except Exception as e:
                study_content[topic] = f"Error generating study material: {e}"

    return study_content

# Streamlit UI
st.set_page_config(layout="wide")
st.title("📚 AI-Powered Study Generator")

with st.sidebar:
    st.header("📌 Input Options")
    subject = st.text_input("Enter Subject:")
    
    if st.button("Generate Syllabus"):
        if subject:
            st.session_state['syllabus'] = generate_syllabus(subject)
        else:
            st.warning("⚠️ Please enter a subject!")
    
    stored_syllabi = [f.replace("syllabus_", "").replace(".txt", "") for f in os.listdir(DATA_DIRS['syllabus']) if f.startswith("syllabus_")]
    if stored_syllabi:
        selected_subject = st.selectbox("Select Subject:", stored_syllabi)
        
        if st.button("View Syllabus"):
            st.session_state['syllabus'] = load_data(DATA_DIRS['syllabus'], f"syllabus_{sanitize_filename(selected_subject)}.txt")
        
        selected_subject_for_plan = st.selectbox("Select Subject for Plan:", stored_syllabi, key="plan_subject")
        duration = st.slider("Select Duration (days):", 1, 30, 7)
        
        if st.button("Generate Lesson Plan"):
            st.session_state['lesson_plan'] = generate_lesson_plan(selected_subject_for_plan, duration)

        day = st.number_input("Select Day (1 - duration):", min_value=1, max_value=duration, value=1)
        
        if 'lesson_plan' in st.session_state:
            topics_for_day = st.session_state['lesson_plan'].get(f"Day {day}", [])
            if st.button(f"Generate Study Material for Day {day}"):
                if selected_subject_for_plan and topics_for_day:
                    st.session_state['study_material'] = generate_study_material(selected_subject_for_plan, day, topics_for_day)
                else:
                    st.warning("⚠️ No topics found for the selected day!")
                

st.header("📌 Generated Content")
if 'syllabus' in st.session_state:
    st.subheader(f"📚 Syllabus for {selected_subject}")
    st.text_area("", st.session_state['syllabus'], height=300)

if 'lesson_plan' in st.session_state:
    st.subheader(f"🗓️ Lesson Plan for {selected_subject_for_plan} - {duration} days")
    st.text_area("", "\n".join([f"{day}: {', '.join(topics)}" for day, topics in st.session_state['lesson_plan'].items()]), height=300)
    
st.sidebar.header("🔍 Get Result for Any Topic")
topic_query = st.sidebar.text_input("Enter Topic:")

if st.sidebar.button("Generate Result"):
    if topic_query:
        try:
            model = genai.GenerativeModel("gemini-1.5-flash")
            response = model.generate_content(f"Give a summarized result about '{topic_query}' including key takeaways.")
            result_text = clean_text(response.text) if hasattr(response, 'text') else "Error: No response from API"
            st.session_state['topic_result'] = result_text
        except Exception as e:
            st.session_state['topic_result'] = f"Error generating result: {e}"
    else:
        st.sidebar.warning("⚠️ Please enter a topic!")

if 'topic_result' in st.session_state:
    st.header(f"📌 Result for: {topic_query}")
    st.text_area("", st.session_state['topic_result'], height=400)
    if st.button("🔊 Speak Result"):
        speak_text(st.session_state['topic_result'])
    if st.button("⏹️ Stop Audio"):
        stop_audio()

if 'study_material' in st.session_state:
    st.subheader(f"📖 Study Material for Day {day}")
    for topic, content in st.session_state['study_material'].items():
        st.subheader(topic)
        st.text_area("", content, height=400)
    
    if st.button("🔊 Read Study Material"):
        speak_text("\n".join(st.session_state['study_material'].values()))
    if st.button("⏹️ Stop Audio"):
        stop_audio()
        
def save_as_pdf(content, filename):
    """Save the given content as a PDF file."""
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    pdf_path = os.path.join("saved_pdfs", filename)
    pdf.output(pdf_path)
    return pdf_path

os.makedirs("saved_pdfs", exist_ok=True)

st.sidebar.header("📌 Save Content as PDF")

if 'syllabus' in st.session_state:
    if st.sidebar.button("Save Syllabus as PDF"):
        filename = f"syllabus_{sanitize_filename(selected_subject)}.pdf"
        pdf_path = save_as_pdf(st.session_state['syllabus'], filename)
        st.sidebar.success(f"Saved as {filename}")
        st.sidebar.download_button("Download Syllabus PDF", pdf_path, filename)

if 'topic_result' in st.session_state:
    if st.sidebar.button("Save Topic Result as PDF"):
        filename = f"topic_result_{sanitize_filename(topic_query)}.pdf"
        pdf_path = save_as_pdf(st.session_state['topic_result'], filename)
        st.sidebar.success(f"Saved as {filename}")
        st.sidebar.download_button("Download Topic Result PDF", pdf_path, filename)

if 'study_material' in st.session_state:
    if st.sidebar.button("Save Study Material as PDF"):
        content = "\n\n".join([f"{topic}\n{text}" for topic, text in st.session_state['study_material'].items()])
        filename = f"study_material_{sanitize_filename(selected_subject_for_plan)}_day{day}.pdf"
        pdf_path = save_as_pdf(content, filename)
        st.sidebar.success(f"Saved as {filename}")
        st.sidebar.download_button("Download Study Material PDF", pdf_path, filename)

        
st.markdown("---")
