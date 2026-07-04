📚 AI Study Assistant

An AI-powered study companion that turns any PDF into an interactive learning tool — chat with your document, generate summaries, quiz yourself, and revise smarter using Retrieval-Augmented Generation (RAG).

Built with Python, Streamlit, Google Gemini API, ChromaDB, and PyPDF.


✨ Features


📄 PDF Upload & Parsing — Extracts and chunks text from any PDF for processing
💬 AI Chat (RAG) — Ask questions about your document and get context-aware answers retrieved from ChromaDB and answered by Gemini
📄 AI Summary — Generates structured, exam-ready study notes (main topics, definitions, key concepts, revision points)
❓ Important Questions — Auto-generates exam-style questions grouped by marks
📝 Interactive MCQs — Generates multiple-choice questions in structured JSON format
🎯 Quiz with Score & Percentage — Take the generated MCQs as a live quiz, get instant scoring, and review correct/incorrect answers
🧠 Flashcards — Flip-style flashcards for active recall, with previous/next navigation
📝 Smart Notes — Condensed, topic-wise bullet notes that are editable before export
📥 Downloads Everywhere — Export Summary, MCQs, and Flashcards as both .txt and .pdf
🌙 Professional UI — Dark themed interface with tabbed navigation, live document stats sidebar, and a polished landing screen
🛡️ Robust Error Handling — Centralized error handling for all AI calls (invalid API key, rate limits, timeouts, empty responses)



🏗️ Tech Stack

ComponentTechnologyUI FrameworkStreamlitLLMGoogle Gemini (gemini-2.5-flash)Vector DatabaseChromaDBPDF ParsingPyPDFPDF Generationfpdf2


📂 Project Structure

study_assistant/
│
├── app.py                     # Main Streamlit application
├── requirements.txt           # Python dependencies
├── .streamlit/
│   ├── secrets.toml           # API keys (gitignored, not committed)
│   └── config.toml            # Custom theme configuration
└── .gitignore


🚀 Getting Started

1. Clone the repository

bashgit clone <your-repo-url>
cd study_assistant

2. Install dependencies

bashpip install -r requirements.txt

3. Add your Gemini API key

Create a file at .streamlit/secrets.toml:

tomlGEMINI_API_KEY = "your_gemini_api_key_here"

Get a free API key from Google AI Studio.


⚠️ Never commit secrets.toml to version control. It's already excluded via .gitignore.



4. Run the app

bashstreamlit run app.py

The app will open at http://localhost:8501.


📖 How It Works


Upload a PDF — text is extracted page by page using PyPDF.
Chunking — the extracted text is split into overlapping chunks (1000 characters, 200 overlap) to preserve context across boundaries.
Indexing — chunks are embedded and stored in a ChromaDB collection for semantic search.
RAG Chat — user questions are matched against the most relevant chunks via ChromaDB similarity search, then passed to Gemini as context for grounded answers.
Content Generation — Summary, Important Questions, MCQs, Flashcards, and Smart Notes are generated via dedicated prompts sent to Gemini, with MCQs/Flashcards parsed as structured JSON.
Quiz Engine — MCQs are rendered as an interactive quiz using Streamlit's session state to track answers, score, and allow retakes.
Export — Summary, MCQs, and Flashcards can be downloaded as plain text or formatted PDF (using a custom word-wrapping PDF generator built on fpdf2).



🛡️ Error Handling

All Gemini API calls are routed through a centralized safe_generate() wrapper that handles:


Invalid or missing API keys
Rate limit / quota errors
Network timeouts
Empty or malformed responses
Invalid JSON from structured generation (MCQs, Flashcards)


This ensures the app degrades gracefully with clear user-facing messages instead of raw exceptions or crashes.


🔮 Potential Future Enhancements


Support for multiple PDFs / document collections
Persistent storage (save quiz history, notes across sessions)
Voice-based Q&A
User authentication and per-user document libraries
Export flashcards to Anki-compatible format



📄 License

This project is open for personal and educational use. Feel free to fork and extend it.


🙏 Acknowledgments

Built using [Streamlit](https://streamlit.io/), [Google Gemini API](https://ai.google.dev/), [ChromaDB](https://www.trychroma.com/), and [PyPDF](https://pypdf.readthedocs.io/).
