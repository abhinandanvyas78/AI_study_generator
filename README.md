# 📚 AI-Powered Personalized Study Generator

An intelligent AI-based web application that automatically generates syllabus, lesson plans, study material, topic summaries, audio narration, and PDF exports using Google Gemini AI and Streamlit.

---

# 🚀 Features

## ✅ AI Syllabus Generation
Generate complete syllabus for any subject using Google Gemini AI.

## ✅ Day-wise Lesson Planning
Automatically distribute topics across selected study duration (1–30 days).

## ✅ AI Study Material
Generate detailed explanations with:
- Definitions
- Key Concepts
- Examples
- Applications

## ✅ Topic Summary Generator
Get instant summarized explanation for any topic.

## ✅ Text-to-Speech (TTS)
Listen to generated content using offline audio narration.

## ✅ PDF Export
Save syllabus, study material, and summaries as PDF.

## ✅ Local Data Storage
Generated content gets stored locally for reuse.

---

# 🛠️ Technologies Used

| Technology | Purpose |
|---|---|
| Python 3.x | Core Programming |
| Streamlit | Web Application UI |
| Google Gemini 1.5 Flash | AI Content Generation |
| pyttsx3 | Text-to-Speech |
| FPDF | PDF Export |
| threading | Background Audio |
| re (Regex) | Text Cleaning |
| os Module | File Handling |

---

Clone Repository
git clone https://github.com/your-username/ai-study-generator.git
cd ai-study-generator
---
Create Virtual Environment
python -m venv venv
venv\Scripts\activate
----
Configure Gemini API Key
genai.configure(api_key="YOUR_GEMINI_API_KEY")
----
Run the Project
streamlit run personalized_ai.py
----

