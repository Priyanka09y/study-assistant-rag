import streamlit as st
import google.generativeai as genai
from pypdf import PdfReader
import chromadb
import json
from fpdf import FPDF

genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
model = genai.GenerativeModel("gemini-2.5-flash")


# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="📚",
    layout="wide"
)
# =====================================================
# CUSTOM CSS
# =====================================================

st.markdown("""
<style>
    /* Overall app background */
    .stApp {
        background-color: #0f1117;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161a23;
        border-right: 1px solid #2a2f3a;
    }

    /* Tabs styling */
    button[data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
        padding: 10px 16px;
    }

    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* Download buttons */
    .stDownloadButton button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #1a1e29;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2a2f3a;
    }

    /* Headings */
    h1, h2, h3 {
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)
st.markdown("""
<style>
    /* Overall app background */
    .stApp {
        background-color: #0f1117;
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #161a23;
        border-right: 1px solid #2a2f3a;
    }

    /* Tabs styling */
    button[data-baseweb="tab"] {
        font-size: 15px;
        font-weight: 600;
        padding: 10px 16px;
    }

    /* Buttons */
    .stButton button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .stButton button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }

    /* Download buttons */
    .stDownloadButton button {
        border-radius: 8px;
        font-weight: 600;
    }

    /* Metric cards */
    div[data-testid="stMetric"] {
        background-color: #1a1e29;
        padding: 15px;
        border-radius: 10px;
        border: 1px solid #2a2f3a;
    }

    /* Headings */
    h1, h2, h3 {
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)


# =====================================================
# TITLE
# =====================================================

st.title("📚 AI Study Assistant")
st.caption("Turn any PDF into an interactive study companion — chat, summarize, quiz, and revise smarter.")

# =====================================================
# FILE UPLOADER
# =====================================================

uploaded_file = st.file_uploader(
    "Upload PDF",
    type=["pdf"],
    key="pdf"
)

if uploaded_file is None:
    st.markdown("---")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.markdown("#### 💬 Chat with your PDF")
        st.caption("Ask questions and get instant, context-aware answers powered by RAG.")

    with col2:
        st.markdown("#### 📝 Auto-generate study material")
        st.caption("Summaries, important questions, MCQs, flashcards, and smart notes — all in one click.")

    with col3:
        st.markdown("#### 🎯 Test yourself")
        st.caption("Take interactive quizzes and track your score instantly.")

    st.markdown("---")

    st.info("👆 Upload a PDF above to get started")

    st.stop()

# =====================================================
# READ PDF
# =====================================================

try:
    pdf = PdfReader(uploaded_file)
    text = ""
    for page in pdf.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
except Exception as e:
    st.error(f"Failed to read PDF: {e}")
    st.stop()

if not text.strip():
    st.error("No readable text found in this PDF. It may be scanned/image-based.")
    st.stop()

st.success("PDF Loaded Successfully")
st.progress(100)

# =====================================================
# SAFE GEMINI CALL WRAPPER
# =====================================================

def safe_generate(prompt: str):
    """
    Wraps Gemini API calls with consistent error handling.
    Returns the response text, or None if it failed (with an st.error shown).
    """
    try:
        response = model.generate_content(prompt)

        if not response or not response.text:
            st.error("The AI returned an empty response. Please try again.")
            return None

        return response.text

    except Exception as e:
        error_msg = str(e).lower()

        if "api key" in error_msg or "permission" in error_msg:
            st.error("Invalid or missing API key. Please check your Gemini API key in secrets.toml.")
        elif "quota" in error_msg or "rate limit" in error_msg:
            st.error("API quota/rate limit reached. Please wait a moment and try again.")
        elif "timeout" in error_msg:
            st.error("Request timed out. Please check your internet connection and try again.")
        else:
            st.error(f"An unexpected error occurred while contacting the AI: {e}")

        return None
# =====================================================
# CREATE CHUNKS
# =====================================================

chunk_size = 1000
overlap = 200

chunks = []
for i in range(0, len(text), chunk_size - overlap):
    chunks.append(text[i:i + chunk_size])

col1, col2 = st.columns(2)
with col1:
    st.metric("Characters", len(text))
with col2:
    st.metric("Chunks", len(chunks))

# =====================================================
# CHROMADB
# =====================================================

client = chromadb.Client()

try:
    client.delete_collection("pdf_data")
except Exception:
    pass

collection = client.create_collection(name="pdf_data")

ids = [str(i) for i in range(len(chunks))]

collection.add(
    documents=chunks,
    ids=ids
)

st.success("Document Indexed Successfully")

with st.sidebar:
    st.markdown("## 📚 AI Study Assistant")
    st.caption("Your AI-powered exam prep companion")

    st.divider()

    if uploaded_file is not None:
        st.markdown("### 📄 Document")
        st.write(f"**File:** {uploaded_file.name}")
        st.write(f"**Characters:** {len(text):,}")
        st.write(f"**Chunks indexed:** {len(chunks)}")
    else:
        st.info("No document uploaded yet")

    st.divider()

    st.markdown("### ✅ Features")
    features = [
        "PDF Upload & Parsing",
        "AI Chat (RAG)",
        "AI Summary",
        "Important Questions",
        "Interactive MCQs + Quiz",
        "Flashcards",
        "Smart Notes",
        "Downloads (TXT/PDF)"
    ]
    for f in features:
        st.write(f"✓ {f}")

    st.divider()

    st.caption("Built with Streamlit, Gemini & ChromaDB")
# =====================================================
# ACTION MENU
# =====================================================

tab_labels = [
    "💬 Ask Questions",
    "📄 Summary",
    "❓ Important Questions",
    "📝 MCQs & Quiz",
    "🧠 Flashcards",
    "📝 Smart Notes"
]

tabs = st.tabs(tab_labels)

# =====================================================
# CONTEXT FOR GEMINI (used by Summary / Important Questions / MCQs)
# =====================================================

summary_context = text[:20000]

# =====================================================
# PDF GENERATION HELPER
# =====================================================

import textwrap


def generate_pdf(title: str, content: str) -> bytes:
    """
    Converts plain text (with optional markdown-style headings)
    into a downloadable PDF as bytes. Manually wraps text to avoid
    FPDF's internal word-wrap crashing/corrupting on long lines.
    """
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    pdf.add_page()

    WRAP_WIDTH = 95  # safe character width for A4 page with 11pt font

    def clean(text: str) -> str:
        # Strip markdown symbols and non-latin1 characters (emojis etc.)
        text = text.replace("**", "").replace("##", "").replace("#", "")
        return text.encode("latin-1", "ignore").decode("latin-1")

    # Title
    pdf.set_font("Helvetica", "B", 16)
    for wrapped in textwrap.wrap(clean(title), WRAP_WIDTH) or [""]:
        pdf.set_x(pdf.l_margin)
        pdf.cell(0, 10, wrapped, ln=True)
    pdf.ln(4)

    pdf.set_font("Helvetica", "", 11)

    for raw_line in content.split("\n"):
        line = raw_line.strip()

        if not line:
            pdf.ln(3)
            continue

        is_heading = line.startswith("#")
        safe_line = clean(line)

        if not safe_line.strip():
            continue

        if is_heading:
            pdf.set_font("Helvetica", "B", 13)
        else:
            pdf.set_font("Helvetica", "", 11)

        wrapped_lines = textwrap.wrap(safe_line, WRAP_WIDTH) or [safe_line]

        for wline in wrapped_lines:
            pdf.set_x(pdf.l_margin)  # force reset position every line
            pdf.cell(0, 7, wline, ln=True)

        if is_heading:
            pdf.set_font("Helvetica", "", 11)

    return bytes(pdf.output(dest="S"))
# =====================================================
# ASK QUESTIONS (RAG)
# =====================================================

with tabs[0]:
    st.subheader("💬 Ask Questions About Your PDF")

    user_question = st.text_input("Type your question here")

    if st.button("Get Answer"):
        if not user_question.strip():
            st.warning("Please enter a question.")
        else:
            try:
                with st.spinner("Searching document..."):
                    results = collection.query(
                        query_texts=[user_question],
                        n_results=3
                    )
                    retrieved_chunks = results["documents"][0]
                    context = "\n\n".join(retrieved_chunks)

                prompt = f"""
You are a helpful study assistant.

Answer the question using ONLY the context below.
If the answer is not in the context, say so clearly instead of guessing.

Context:
{context}

Question:
{user_question}
"""

                with st.spinner("Generating answer..."):
                    answer_text = safe_generate(prompt)

                if answer_text:
                    st.success("Answer:")
                    st.markdown(answer_text)

            except Exception as e:
                st.error(f"Something went wrong while answering: {e}")

# =====================================================
#  GENERATE SUMMARY
# =====================================================

with tabs[1]:
    st.subheader("📄 AI Summary")

    if st.button("Generate Summary"):
        prompt = f"""
You are an expert university professor.

Read the document carefully and generate COMPLETE study notes.

Your output MUST contain:

# 📄 Short Summary

# 📚 Main Topics

# 📖 Important Definitions

# 💡 Important Concepts
Explain every concept in detail.

# ⭐ Key Points
Use bullet points.

# 🎯 GTU Exam Notes
Mention:
- Frequently Asked Topics
- 2 Marks
- 5 Marks
- 7 Marks
- 10 Marks

# 🔥 Last Minute Revision
Give 10 one-line revision points.

Document:

{summary_context}
"""
        with st.spinner("Generating Summary..."):
            summary_result = safe_generate(prompt)

        if summary_result:
            st.session_state["summary_text"] = summary_result
            st.success("Summary Generated")

    if "summary_text" in st.session_state:

        st.markdown(st.session_state["summary_text"])

        st.divider()
        st.subheader("📥 Download Summary")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📥 Download as TXT",
                st.session_state["summary_text"],
                file_name="summary.txt",
                mime="text/plain"
            )

        with col2:
            try:
                pdf_bytes = generate_pdf("AI Study Summary", st.session_state["summary_text"])
                st.download_button(
                    "📥 Download as PDF",
                    pdf_bytes,
                    file_name="summary.pdf",
                    mime="application/pdf"
                )
            except Exception as e:
                st.error(f"Failed to generate PDF: {e}")
# =====================================================
# IMPORTANT QUESTIONS
# =====================================================

with tabs[2]:
    st.subheader("❓ Important Questions")

    if st.button("Generate Important Questions"):
        prompt = f"""
You are an expert exam paper setter.

Based on the document below, generate a list of the most IMPORTANT
exam-style questions a student should prepare, grouped by marks:

# 2 Marks Questions
# 5 Marks Questions
# 7 Marks Questions
# 10 Marks Questions

Document:

{summary_context}
"""
        with st.spinner("Generating Important Questions..."):
            iq_result = safe_generate(prompt)

        if iq_result:
            st.success("Important Questions Generated")
            st.markdown(iq_result)

# =====================================================
# GENERATE MCQs (JSON) + QUIZ
# =====================================================

with tabs[3]:
    st.subheader("📝 Generate MCQs")

    num_mcqs = st.slider("Number of MCQs", 5, 20, 10)

    if st.button("Generate MCQs"):
        prompt = f"""
You are an expert exam paper setter.

Generate exactly {num_mcqs} multiple choice questions based on the document below.

Return ONLY valid JSON, no extra text, no markdown formatting, in this exact structure:

[
  {{
    "question": "...",
    "options": ["A", "B", "C", "D"],
    "answer": "the correct option text",
    "explanation": "short explanation"
  }}
]

Document:

{summary_context}
"""
        with st.spinner("Generating MCQs..."):
            mcq_response_text = safe_generate(prompt)

        if mcq_response_text:
            raw_text = mcq_response_text.strip()

            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                raw_text = raw_text.replace("json", "", 1).strip()

            try:
                mcqs = json.loads(raw_text)

                st.session_state["mcqs"] = mcqs
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_answers"] = {}

                st.success(f"Generated {len(mcqs)} MCQs")

            except json.JSONDecodeError:
                st.error("Gemini returned invalid JSON. Please try again.")

# =====================================================    
## QUIZ DISPLAY
# =====================================================
    if "mcqs" in st.session_state:

        st.divider()
        st.subheader("🎯 Take the Quiz")

        mcqs = st.session_state["mcqs"]

        # Make sure state dicts exist (in case of app rerun/session issues)
        if "quiz_answers" not in st.session_state:
            st.session_state["quiz_answers"] = {}
        if "quiz_submitted" not in st.session_state:
            st.session_state["quiz_submitted"] = False

        # Render each question with radio buttons
        for i, mcq in enumerate(mcqs):
            st.markdown(f"**Q{i + 1}. {mcq['question']}**")

            selected = st.radio(
                label="Select an answer",
                options=mcq["options"],
                index=None,
                key=f"quiz_q_{i}",
                label_visibility="collapsed"
            )

            st.session_state["quiz_answers"][i] = selected
            st.write("")  # spacing

        # Submit button
        if not st.session_state["quiz_submitted"]:
            if st.button("✅ Submit Quiz"):
                unanswered = [
                    i + 1 for i in range(len(mcqs))
                    if st.session_state["quiz_answers"].get(i) is None
                ]
                if unanswered:
                    st.warning(
                        f"Please answer all questions before submitting. "
                        f"Missing: Q{', Q'.join(map(str, unanswered))}"
                    )
                else:
                    st.session_state["quiz_submitted"] = True
                    st.rerun()

# =====================================================       
# RESULTS
# =====================================================
        if st.session_state["quiz_submitted"]:

            score = 0
            total = len(mcqs)

            for i, mcq in enumerate(mcqs):
                user_ans = st.session_state["quiz_answers"].get(i)
                if user_ans == mcq["answer"]:
                    score += 1

            percentage = round((score / total) * 100, 2) if total > 0 else 0

            st.divider()
            st.subheader("📊 Quiz Results")

            col1, col2 = st.columns(2)
            with col1:
                st.metric("Score", f"{score} / {total}")
            with col2:
                st.metric("Percentage", f"{percentage}%")

            if percentage >= 80:
                st.success("Excellent work! 🎉")
            elif percentage >= 50:
                st.info("Good job, but there's room to improve. 📘")
            else:
                st.warning("You should review the material again. 📖")

            st.divider()
            st.subheader("📋 Answer Review")

            for i, mcq in enumerate(mcqs):
                user_ans = st.session_state["quiz_answers"].get(i)
                correct_ans = mcq["answer"]
                is_correct = user_ans == correct_ans

                icon = "✅" if is_correct else "❌"
                st.markdown(f"{icon} **Q{i + 1}. {mcq['question']}**")
                st.write(f"Your answer: {user_ans}")
                if not is_correct:
                    st.write(f"Correct answer: {correct_ans}")
                st.caption(mcq.get("explanation", ""))
                st.divider()

            if st.button("🔄 Retake Quiz"):
                st.session_state["quiz_submitted"] = False
                st.session_state["quiz_answers"] = {}
                for i in range(len(mcqs)):
                    st.session_state.pop(f"quiz_q_{i}", None)
                st.rerun()
# =====================================================
# DOWNLOAD MCQs
# =====================================================
        st.divider()
        st.subheader("📥 Download MCQs")

        def build_mcq_text(mcqs_list) -> str:
            lines = []
            for i, mcq in enumerate(mcqs_list, start=1):
                lines.append(f"Q{i}. {mcq['question']}")
                for opt in mcq["options"]:
                    lines.append(f"   - {opt}")
                lines.append(f"   Answer: {mcq['answer']}")
                if mcq.get("explanation"):
                    lines.append(f"   Explanation: {mcq['explanation']}")
                lines.append("")  # blank line between questions
            return "\n".join(lines)

        mcq_text = build_mcq_text(mcqs)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📥 Download as TXT",
                mcq_text,
                file_name="mcqs.txt",
                mime="text/plain",
                key="mcq_download_txt"
            )

        with col2:
            try:
                mcq_pdf_bytes = generate_pdf("MCQ Practice Set", mcq_text)
                st.download_button(
                    "📥 Download as PDF",
                    mcq_pdf_bytes,
                    file_name="mcqs.pdf",
                    mime="application/pdf",
                    key="mcq_download_pdf"
                )
            except Exception as e:
                st.error(f"Failed to generate MCQ PDF: {e}")

# =====================================================
#  FLASHCARDS
# =====================================================

with tabs[4]:
    st.subheader("🧠 Flashcards")

    num_cards = st.slider("Number of Flashcards", 5, 20, 10)

    if st.button("Generate Flashcards"):
        prompt = f"""
You are an expert study coach creating flashcards for active recall.

Generate exactly {num_cards} flashcards based on the document below.

Return ONLY valid JSON, no extra text, no markdown formatting, in this exact structure:

[
  {{
    "front": "A short question or term",
    "back": "A concise, clear answer or definition"
  }}
]

Keep the "front" short (a term or question).
Keep the "back" concise (1-3 sentences max).

Document:

{summary_context}
"""
        with st.spinner("Generating Flashcards..."):
            flashcard_response_text = safe_generate(prompt)

        if flashcard_response_text:
            raw_text = flashcard_response_text.strip()

            if raw_text.startswith("```"):
                raw_text = raw_text.strip("`")
                raw_text = raw_text.replace("json", "", 1).strip()

            try:
                flashcards = json.loads(raw_text)

                st.session_state["flashcards"] = flashcards
                st.session_state["flashcard_index"] = 0
                st.session_state["flashcard_flipped"] = False

                st.success(f"Generated {len(flashcards)} flashcards")

            except json.JSONDecodeError:
                st.error("Gemini returned invalid JSON. Please try again.")

# =====================================================
# FLASHCARD VIEWER
# =====================================================
    if "flashcards" in st.session_state:

        flashcards = st.session_state["flashcards"]
        total = len(flashcards)
        idx = st.session_state["flashcard_index"]

        st.divider()
        st.caption(f"Card {idx + 1} of {total}")

        card = flashcards[idx]
        card_text = card["back"] if st.session_state["flashcard_flipped"] else card["front"]
        card_label = "Answer" if st.session_state["flashcard_flipped"] else "Question"

        # Card display
        st.markdown(
            f"""
            <div style="
                background-color:#1e1e2f;
                color:white;
                padding:40px;
                border-radius:15px;
                text-align:center;
                font-size:20px;
                min-height:150px;
                display:flex;
                align-items:center;
                justify-content:center;
            ">
                {card_text}
            </div>
            """,
            unsafe_allow_html=True
        )
        st.caption(card_label)

        st.write("")

        # Controls
        col1, col2, col3 = st.columns([1, 1, 1])

        with col1:
            if st.button("⬅️ Previous", use_container_width=True):
                if idx > 0:
                    st.session_state["flashcard_index"] -= 1
                    st.session_state["flashcard_flipped"] = False
                    st.rerun()

        with col2:
            if st.button("🔄 Flip Card", use_container_width=True):
                st.session_state["flashcard_flipped"] = not st.session_state["flashcard_flipped"]
                st.rerun()

        with col3:
            if st.button("Next ➡️", use_container_width=True):
                if idx < total - 1:
                    st.session_state["flashcard_index"] += 1
                    st.session_state["flashcard_flipped"] = False
                    st.rerun()

        st.divider()

        # Download flashcards
        st.subheader("📥 Download Flashcards")

        def build_flashcard_text(cards_list) -> str:
            lines = []
            for i, c in enumerate(cards_list, start=1):
                lines.append(f"{i}. Q: {c['front']}")
                lines.append(f"   A: {c['back']}")
                lines.append("")
            return "\n".join(lines)

        flashcard_text = build_flashcard_text(flashcards)

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📥 Download as TXT",
                flashcard_text,
                file_name="flashcards.txt",
                mime="text/plain",
                key="flashcard_download_txt"
            )

        with col2:
            try:
                flashcard_pdf_bytes = generate_pdf("Flashcards", flashcard_text)
                st.download_button(
                    "📥 Download as PDF",
                    flashcard_pdf_bytes,
                    file_name="flashcards.pdf",
                    mime="application/pdf",
                    key="flashcard_download_pdf"
                )
            except Exception as e:
                st.error(f"Failed to generate flashcards PDF: {e}")
# =====================================================
# SMART NOTES
# =====================================================

with tabs[5]:
    st.subheader("📝 Smart Notes")

    st.caption("Condensed, topic-wise notes for quick daily revision — editable before download.")

    if st.button("Generate Smart Notes"):
        prompt = f"""
You are a study coach creating quick-revision notes.

Read the document and generate SHORT, topic-wise bullet-point notes.

Rules:
- Organize by clear topic headings (use "#" before each heading)
- Under each heading, use short bullet points (one line each)
- No long paragraphs — keep every point crisp and exam-ready
- Focus only on the most important facts, formulas, and definitions

Document:

{summary_context}
"""
        with st.spinner("Generating Smart Notes..."):
            notes_result = safe_generate(prompt)

        if notes_result:
            st.session_state["smart_notes"] = notes_result
            st.success("Smart Notes Generated")

# -------------------------------------------------
# EDITABLE NOTES + DOWNLOAD
# -------------------------------------------------

    if "smart_notes" in st.session_state:

        st.divider()

        edited_notes = st.text_area(
            "✏️ You can edit your notes below before downloading:",
            value=st.session_state["smart_notes"],
            height=400,
            key="smart_notes_editor"
        )

        # Keep session state in sync with edits
        st.session_state["smart_notes"] = edited_notes

        st.divider()
        st.subheader("📥 Download Smart Notes")

        col1, col2 = st.columns(2)

        with col1:
            st.download_button(
                "📥 Download as TXT",
                edited_notes,
                file_name="smart_notes.txt",
                mime="text/plain",
                key="notes_download_txt"
            )

        with col2:
            try:
                notes_pdf_bytes = generate_pdf("Smart Notes", edited_notes)
                st.download_button(
                    "📥 Download as PDF",
                    notes_pdf_bytes,
                    file_name="smart_notes.pdf",
                    mime="application/pdf",
                    key="notes_download_pdf"
                )
            except Exception as e:
                st.error(f"Failed to generate notes PDF: {e}")