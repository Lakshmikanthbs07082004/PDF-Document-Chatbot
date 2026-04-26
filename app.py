"""
app.py — Streamlit UI for the PDF Document Chatbot.

Run with: streamlit run app.py
"""

import logging
import time
from datetime import datetime

import streamlit as st
from google import genai

import config
from utils.document_loader import load_pdf
from utils.chunker import chunk_text
from utils.embedder import embed_chunks
from utils.retriever import retrieve_top_chunks
from utils.validator import validate_file, validate_query

logger = logging.getLogger(__name__)

# ── Page config (must be first st call) ────────────────────────
st.set_page_config(page_title="PDF Document Chatbot", page_icon="📄", layout="wide")

# ── Custom CSS ─────────────────────────────────────────────────
st.markdown("""<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Inter', sans-serif; }
.main-header { background: linear-gradient(135deg, #667eea, #764ba2);
  padding: 2rem; border-radius: 16px; color: white; text-align: center;
  margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(102,126,234,0.3); }
.main-header h1 { margin:0; font-size:2.2rem; font-weight:700; }
.main-header p { margin:0.5rem 0 0 0; opacity:0.9; }
.status-ready { background:#dcfce7; color:#166534; padding:0.4rem 1rem;
  border-radius:20px; font-weight:600; font-size:0.85rem; text-align:center; }
.status-waiting { background:#fef3c7; color:#92400e; padding:0.4rem 1rem;
  border-radius:20px; font-weight:600; font-size:0.85rem; text-align:center; }
.stats-card { background:white; border-radius:12px; padding:1rem; margin:0.5rem 0;
  box-shadow:0 2px 8px rgba(0,0,0,0.04); border:1px solid #e2e8f0; }
</style>""", unsafe_allow_html=True)

# ── Session state defaults ─────────────────────────────────────
for k, v in {"chunks": [], "chat_history": [], "pdf_name": "",
             "pdf_pages": 0, "pdf_text": "", "processing_done": False}.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── API key check ──────────────────────────────────────────────
if not config.check_keys():
    st.error("⚠️ **GEMINI_API_KEY not configured.** Copy `.env.example` → `.env` and add your key.")
    st.stop()

# ── Header ─────────────────────────────────────────────────────
st.markdown('<div class="main-header"><h1>📄 PDF Document Chatbot</h1>'
            '<p>Upload a PDF and ask questions — powered by Google Gemini AI</p></div>',
            unsafe_allow_html=True)

# ━━━━━━━━━━━ SIDEBAR ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
with st.sidebar:
    st.markdown("## 📂 Upload Document")
    uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"],
                                     help="Maximum file size: 20 MB")

    if uploaded_file is not None:
        file_bytes: bytes = uploaded_file.getvalue()
        file_name: str = uploaded_file.name
        if file_name != st.session_state["pdf_name"]:
            valid, err = validate_file(file_name, len(file_bytes))
            if not valid:
                st.error(f"❌ {err}")
            else:
                with st.spinner("🔄 Processing PDF…"):
                    try:
                        text, pages = load_pdf(file_bytes)
                        if not text.strip():
                            st.error("❌ No extractable text found (scanned PDF?).")
                        else:
                            chunks = embed_chunks(chunk_text(text))
                            st.session_state.update(chunks=chunks, pdf_name=file_name,
                                pdf_pages=pages, pdf_text=text, processing_done=True,
                                chat_history=[])
                            st.success(f"✅ **{file_name}** processed!")
                    except (ValueError, RuntimeError) as exc:
                        st.error(f"❌ {exc}")
                    except Exception as exc:
                        logger.exception("Unexpected error during PDF processing.")
                        st.error(f"❌ Unexpected error: {exc}")

    st.markdown("---")
    st.markdown("## 📊 Status")
    if st.session_state["processing_done"]:
        st.markdown('<div class="status-ready">✅ Ready to Chat</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="stats-card"><b>📄</b> {st.session_state["pdf_name"]}<br>'
                    f'<b>📑</b> {st.session_state["pdf_pages"]} pages<br>'
                    f'<b>🧩</b> {len(st.session_state["chunks"])} chunks<br>'
                    f'<b>💬</b> {len(st.session_state["chat_history"])} messages</div>',
                    unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-waiting">⏳ Waiting for PDF</div>', unsafe_allow_html=True)

    if st.session_state["chat_history"]:
        st.markdown("---")
        lines = [f"Chat History — {st.session_state['pdf_name']}", "=" * 50]
        for m in st.session_state["chat_history"]:
            lines.append(f"\n[{'YOU' if m['role']=='user' else 'BOT'}]\n{m['content']}")
        st.download_button("📥 Download Chat", "\n".join(lines),
                           f"chat_{datetime.now():%Y%m%d_%H%M%S}.txt", "text/plain",
                           use_container_width=True)

    st.markdown("---")
    if st.button("🗑️ Clear & Reset", use_container_width=True):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ━━━━━━━━━━━ CHAT AREA ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
for msg in st.session_state["chat_history"]:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

if prompt := st.chat_input("Ask a question about your PDF…"):
    if not st.session_state["processing_done"]:
        st.error("⚠️ Please upload a PDF file first.")
    else:
        valid, err = validate_query(prompt)
        if not valid:
            st.error(f"⚠️ {err}")
        else:
            st.session_state["chat_history"].append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)
            with st.chat_message("assistant"):
                with st.spinner("🤔 Thinking…"):
                    try:
                        top_chunks = retrieve_top_chunks(prompt, st.session_state["chunks"])
                        ctx = "\n\n---\n\n".join(
                            f"[Chunk {c['index']+1}] (score: {c['score']:.2f})\n{c['content']}"
                            for c in top_chunks)
                        full_prompt = (f"{config.SYSTEM_PROMPT}\n\n"
                                       f"--- DOCUMENT CONTEXT ---\n{ctx}\n\n"
                                       f"--- QUESTION ---\n{prompt}")
                        client = genai.Client(api_key=config.GEMINI_API_KEY)

                        # Retry up to 3 times on temporary server errors (503)
                        answer = None
                        for attempt in range(1, 4):
                            try:
                                resp = client.models.generate_content(
                                    model=config.GENERATION_MODEL,
                                    contents=full_prompt)
                                answer = resp.text
                                break
                            except Exception as gen_exc:
                                if ("503" in str(gen_exc) or "UNAVAILABLE" in str(gen_exc)) and attempt < 3:
                                    st.warning(f"⏳ Server busy, retrying ({attempt}/3)…")
                                    time.sleep(10 * attempt)
                                else:
                                    raise gen_exc

                        # ── Display the structured answer ──
                        st.markdown(answer)

                        # ── Display sources in a collapsible expander ──
                        with st.expander("📚 **View Sources**", expanded=False):
                            for rank, c in enumerate(top_chunks[:3], start=1):
                                relevance = c['score'] * 100
                                preview = c['content'][:200].replace('\n', ' ').strip()
                                st.markdown(
                                    f"**Source {rank}** &nbsp;·&nbsp; "
                                    f"Relevance: `{relevance:.0f}%`\n\n"
                                    f"> {preview}…"
                                )
                                if rank < min(3, len(top_chunks)):
                                    st.markdown("---")

                        # ── Save to chat history ──
                        st.session_state["chat_history"].append(
                            {"role": "assistant", "content": answer})
                    except (RuntimeError, Exception) as exc:
                        st.error(f"❌ Error: {exc}")
                        logger.exception("Chat error")
