# 📄 PDF Document Chatbot

An intelligent **PDF Document Chatbot** built with **Streamlit** and **Google Gemini AI** that lets you upload PDF files and have natural-language conversations about their content. The system uses Retrieval-Augmented Generation (RAG) to extract, chunk, embed, and retrieve relevant context before generating accurate, citation-backed answers.

---

## ✨ Features

- **PDF Upload & Parsing** — Upload any PDF (up to 200 MB) and extract text automatically using PyPDF2.
- **Smart Chunking** — Documents are split into overlapping chunks (1 000 chars, 200 overlap) for optimal embedding quality.
- **Semantic Embeddings** — Each chunk is embedded locally using `all-MiniLM-L6-v2` (sentence-transformers) — no API calls, no quotas, works offline.
- **Cosine-Similarity Retrieval** — User queries are embedded and matched against document chunks to surface the most relevant context.
- **AI-Powered Answers** — Retrieved chunks are fed to `gemini-2.5-flash-lite` which generates structured, well-formatted answers using bold, bullet points, and headings.
- **Collapsible Sources** — Each answer includes an expandable "📚 View Sources" section showing the top-3 matching document excerpts with relevance scores.
- **Auto-Retry on Server Errors** — The app automatically retries up to 3 times with backoff if the Gemini API returns a temporary 503 error.
- **Chat History** — Full conversation history is maintained in-session and can be downloaded as a `.txt` file.
- **Input Validation** — File type, file size, and query length are validated to ensure robust operation.
- **Modern UI** — A polished, gradient-themed Streamlit interface with status cards, real-time processing indicators, and responsive layout.

---

## 🏗️ Architecture

```
User ──▶ Streamlit UI (app.py)
              │
              ├── Upload PDF
              │       │
              │       ▼
              │   document_loader.py  ──▶  Extract text & page count
              │       │
              │       ▼
              │   chunker.py          ──▶  Split text into overlapping chunks
              │       │
              │       ▼
              │   embedder.py         ──▶  Generate embeddings locally (sentence-transformers)
              │
              ├── Ask Question
              │       │
              │       ▼
              │   validator.py        ──▶  Validate query length & content
              │       │
              │       ▼
              │   retriever.py        ──▶  Cosine similarity → Top-K chunks
              │       │
              │       ▼
              │   Gemini LLM          ──▶  Generate structured answer (with auto-retry)
              │
              └── Display Answer + Collapsible Sources
```

---

## 🚀 Getting Started

### Prerequisites

- **Python 3.10+**
- A **Google Gemini API key** (for answer generation only) — get one free at [Google AI Studio](https://aistudio.google.com/app/apikey)
- **Internet connection** on first run to download the embedding model (~90 MB, cached locally afterwards)

### 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/pdf-document-chatbot.git
cd pdf-document-chatbot
```

### 2. Create & Activate a Virtual Environment

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS / Linux
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
# Copy the example file
cp .env.example .env
```

Open `.env` and add your Gemini API key:

```env
GEMINI_API_KEY=your-actual-api-key-here
```

### 5. Run the Application

```bash
streamlit run app.py
```

The app will open in your browser at **http://localhost:8501**.

---

## 📖 Usage

1. **Upload a PDF** — Use the sidebar file uploader to select a PDF document.
2. **Wait for processing** — The app extracts text, chunks it, and generates embeddings (progress shown in the sidebar).
3. **Ask questions** — Type your question in the chat input at the bottom of the page.
4. **Review answers** — The chatbot responds with a structured AI-generated answer. Click **📚 View Sources** to see the matching document excerpts.
5. **Download chat** — Click **📥 Download Chat** in the sidebar to save the conversation.
6. **Reset** — Click **🗑️ Clear & Reset** to start fresh with a new document.

---

## 📁 Project Structure

```
pdf-document-chatbot/
├── app.py                  # Main Streamlit application (UI + chat logic)
├── config.py               # Centralised configuration & constants
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variable template
├── .env                    # Your API keys (not committed)
├── test_validation.py      # Automated validation tests
├── utils/
│   ├── __init__.py         # Package initialiser
│   ├── document_loader.py  # PDF text extraction (PyPDF2)
│   ├── chunker.py          # Text chunking with overlap
│   ├── embedder.py         # Local embedding generation (sentence-transformers)
│   ├── retriever.py        # Cosine-similarity retrieval
│   └── validator.py        # File & query input validation
└── README.md               # This file
```

---

## ⚙️ Configuration

All tuneable parameters are centralised in [`config.py`](config.py):

| Parameter | Default | Description |
|---|---|---|
| `GENERATION_MODEL` | `gemini-2.5-flash-lite` | Gemini model for answer generation |
| `EMBEDDING_MODEL` | `all-MiniLM-L6-v2` | Local sentence-transformers model for embeddings |
| `CHUNK_SIZE` | `1000` | Characters per chunk |
| `CHUNK_OVERLAP` | `200` | Overlap between consecutive chunks |
| `TOP_K` | `5` | Number of chunks retrieved per query |
| `MAX_FILE_SIZE_BYTES` | `20 MB` | Maximum upload file size |
| `MAX_QUERY_LENGTH` | `2000` | Maximum query length (characters) |
| `MIN_QUERY_LENGTH` | `3` | Minimum query length (characters) |

---

## 🧪 Testing

Run the validation test suite with:

```bash
pytest test_validation.py -v
```

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Streamlit |
| **LLM** | Google Gemini (`gemini-2.5-flash-lite`) |
| **Embeddings** | sentence-transformers (`all-MiniLM-L6-v2`) — runs locally |
| **PDF Parsing** | PyPDF2 |
| **Vector Similarity** | NumPy (cosine similarity) |
| **Environment Config** | python-dotenv |
| **Testing** | pytest |

---

## 🔒 Security Notes

- Your API key is stored locally in `.env` and **never committed** to version control.
- Add `.env` to your `.gitignore` to prevent accidental exposure.
- File uploads are validated for type and size before processing.

---

## 📝 License

This project is developed for educational and academic purposes.

---

<p align="center">
  Built with ❤️ using <a href="https://streamlit.io">Streamlit</a> and <a href="https://ai.google.dev">Google Gemini AI</a>
</p>
